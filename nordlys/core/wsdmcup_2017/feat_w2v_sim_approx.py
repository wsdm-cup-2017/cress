"""Implements a feature with cosine similarity among the 300-dim Google News w2v vectors.

@author: Dario Garigliotti
"""

from collections import Counter
from operator import itemgetter

from nordlys.config import MONGO_HOST, MONGO_DB, MONGO_COLLECTION_WORD2VEC
from nordlys.core.storage.mongo import Mongo
from nordlys.logic.features.word2vec.word2vec import Word2Vec
from nordlys.core.utils.file_utils import FileUtils
from nordlys.core.wsdmcup_2017.config import *  # we know this module so no danger, but be careful ;)
from nordlys.core.wsdmcup_2017.wsdmcup_ids import WSDMCupIDs
from nordlys.core.wsdmcup_2017.feat_termstats import cos_sim

WP_PREFIX = "wikipedia_"


class FeaturesW2VSimApprox(object):
    """Implements our simCosW2VPG feature, i.e., the cosine similarity between the profession \
    (centroid of TFIDF-weighted word2vec vectors of top-K profession terms) and person \
    (centroid of TF-weighted word2vec vectors of significant terms of first Wikipedia paragraph) vectors.
    """

    # Formula for feature computation:
    #
    # $cos(\vec{t}^{w2v}_{pe}, \vec{t}^{w2v}_{pr, k})$, where:
	# $$\vec{t}^{w2v}_{pe} = \sum_{t \in PG_{1}(pe) ~:~ tf(t) \geq 2 ~\wedge~ |t| \geq 4} tf(t, pe) w2v(t)$$
	# $$\vec{t}^{w2v}_{pr, k} = \sum_{t \in T_k(pr)} w(t, pr) w2v(t)$$
	# (note that using these unnormalized sums in the computation of $cos()$ is equivalent to use the actual centroids).

    def __init__(self):
        mongo = Mongo(MONGO_HOST, MONGO_DB, MONGO_COLLECTION_WORD2VEC)
        self.__word2vec = Word2Vec(mongo)

    @property
    def word2vec(self):
        return self.__word2vec

    def __increase(self, v, term, weight):
        """Increases v by weight times term.

        :param v:
        :param term:
        :param weight:
        :return:
        """
        if self.word2vec.contains_word(term):
            term_v = self.word2vec.get_vector(term)
            for i in range(len(v)):
                v[i] += term_v[i] * weight

    def __load_items_stats(self, items_tfidf_fpath):
        """Loads pre-computed tf-idf stats for items.

        :param items_tfidf_fpath:
        :return:
        """
        item_term_weights = {}

        for line in FileUtils.read_file_as_list(items_tfidf_fpath):
            item, term, _, _, weight = line.split("\t", maxsplit=4)
            if len(term) < 4:  # avoid short terms
                continue

            # some cleanings
            if term.startswith("_"):
                term = term[1:]
            if term.endswith("_"):
                term = term[:-1]
            if term.startswith(WP_PREFIX):  # it's a person name
                term = term.split(WP_PREFIX)[-1]  # remove prefix
                term = "_".join([word[0].upper() + word[1:] for word in term.split("_")])  # capitalize every word

            item_d = item_term_weights.get(item, {})
            item_d[term] = float(weight)
            item_term_weights[item] = item_d

        return item_term_weights

    def get_vector(self, terms_weights):
        """Gets a 300-dim vector as result of a weighted sum over the terms.

        :param terms_weights: dict from terms to their weights.
        :return:
        """
        v = self.word2vec.get_zeros_vector(self.word2vec.dimension)

        for term, weight in terms_weights.items():
            self.__increase(v, term, weight)

        return v

    def get_all_features_approx(self, all_items_fpath, items_tfidf_fpath, first_snippets_fpath, person_items_fpath,
                                dest_fpath):
        """Core function for generating into output_file the features, with person-item data from kb_file.

        :param all_items_fpath: path to the file with all items (e.g. 'professions' named file).
        :param items_tfidf_fpath: path to the file with item tf-idf stats.
        :param first_snippets_fpath: path to the file with first snippets.
        :param person_items_fpath: path to the file with person items (a '.kb'-extension file).
        :param dest_fpath: destination file path.
        :return:
        """
        wcup_ids = WSDMCupIDs()

        # -------
        # Get persons vectors

        # Load person-to-snippet mapping
        persons_to_vec = {}
        for line in FileUtils.read_file_as_list(first_snippets_fpath):
            person, snippet = line.split("\t")
            person = person.split("<{}".format(DBPEDIA_URI_PREFIX))[-1].split(">")[0].replace("_", " ")

            c = {k: v for k, v in Counter(snippet.split()).items() if k not in STOPWORDS and v >= 2}  # min freq = 2
            total = sum([v for k, v in c.items()])
            c = {k: round(v / total, 4) for k, v in c.items()}
            v = self.get_vector(c)
            persons_to_vec[person] = v
        print("Get persons vectors... OK.")

        # -------
        # Get profession vectors

        # Load professions tf-idf
        # dict from each item (e.g. professions) to its term-to-weight dict
        item_term_weights = self.__load_items_stats(items_tfidf_fpath)
        prof_to_vec = {}
        for raw_item in FileUtils.read_file_as_list(all_items_fpath):
            # for professions
            item = wcup_ids.get_id_from_prof(raw_item)  # DON'T FORGET!
            v = self.get_vector(item_term_weights.get(item, {}))

            # ---
            # Alternative vector version, using the w2v vector when it exists, without top-K terms
            #
            # if not self.word2vec.contains_word(item):  # build our own vector with top-K terms for that item
            #     v = self.get_vector(item_term_weights.get(item, {}))
            # else:  # take advantage of an already well-represented vector present in the w2v collection
            #     v = self.word2vec.get_vector(item)
            # ---
            prof_to_vec[item] = v
        print("Get profession vectors... OK.")

        # -------
        # Load persons-to-professions and get cos sims
        person_to_prof_to_cos = {}  # e.g. person-to-profession-to-cos_sim
        for line in FileUtils.read_file_as_list(person_items_fpath):
            person, item = line.split("\t", maxsplit=1)
            item = wcup_ids.get_id_from_prof(item)  # DON'T FORGET!

            if person not in person_to_prof_to_cos:
                person_to_prof_to_cos[person] = {}

            person_vec = persons_to_vec.get(person, self.word2vec.get_zeros_vector(self.word2vec.dimension))
            prof_vec = prof_to_vec.get(item, self.word2vec.get_zeros_vector(self.word2vec.dimension))

            feat_value = cos_sim(person_vec, prof_vec)
            person_to_prof_to_cos[person][item] = feat_value
        pass

        with open(dest_fpath, "w") as f_out:
            f_out.write("person\tprofession\tsimCos_w2v_aggr_100\n")
            for person, data in sorted(person_to_prof_to_cos.items()):  # sorted by person full name
                for item, sim in sorted(data.items(), key=itemgetter(1), reverse=True):  # sorted decreasingly by sim
                    f_out.write("{}\t{}\t{}\n".format(wcup_ids.get_id_from_person(person), item, sim))


def main():
    feat = FeaturesW2VSimApprox()
    items_tfidf_fpath = TF_IDF_F  # professions (no var is needed, just to be able to comment what items are about :P)
    feat.get_all_features_approx(PROFESSIONS_F, items_tfidf_fpath, FIRST_WP_PG_F, PROF_KB_F,
                                 PROF_APPROX_W2V_AGGR_COS_SIM_F)


if __name__ == '__main__':
    main()
