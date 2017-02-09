"""
Generating feature for cos sim of person vector vs profession vector, using for both the aggregated w2v vectors.

@author Krisztian Balog
@author Shuo Zhang
@author Dario Garigliotti

"""

from nordlys.core.retrieval.elastic_cache import ElasticCache
from nordlys.core.utils.file_utils import FileUtils
from nordlys.core.wsdmcup_2017.feat_w2v_sim_approx import FeaturesW2VSimApprox
from nordlys.core.wsdmcup_2017.feat_termstats import cos_sim
from nordlys.core.wsdmcup_2017.config import *


class FeaturesW2VSim(object):
    """Implements our simCosW2V feature, i.e., the cosine similarity between the profession and person vectors, \
    where the profession (resp. person) vector is the centroid of TFIDF-weighted word2vec vectors of top-K profession \
    (resp. person) terms.
    """

    # Formula for feature computation:
    #
    # $cos(\vec{t}^{w2v}_{pe, k}, \vec{t}^{w2v}_{pr, k})$, where for item $\in \{pe, pr\}$:
    # $$\vec{t}^{w2v}_{item, k} = \sum_{t \in T_k(item)} w(t, item) w2v(t)$$
    # (note that using these unnormalized sums in the computation of $cos()$ is equivalent to use the actual centroids).

    CONTENT_FIELD = "content"
    PROF_FIELD = "professions"
    K_VALUES = [10, 50, 100, 200, 500, 1000]
    MAX_K = max(K_VALUES)

    def __init__(self, index_name=WP_ST_INDEX_ID):
        self.__elastic = ElasticCache(index_name)
        self.__stats = None

    def load_termstats(self, input_file):
        self.__stats = {}
        with FileUtils.open_file_by_type(input_file) as f_in:
            rank = 0
            last_prof = None
            for line in f_in:
                prof, term, tf, df, tfidf = line.strip().split("\t")
                if prof != last_prof:
                    rank = 0
                    last_prof = prof
                rank += 1
                if term in STOPWORDS:  # filter stopwords
                    continue
                if term.startswith("fb_"):  # filter entity terms
                    continue
                if prof not in self.__stats:
                    self.__stats[prof] = {}
                self.__stats[prof][term] = {"tf": int(tf), "df": int(df), "tfidf": float(tfidf), "rank": rank}

    def get_person_tf(self, person_id):
        """Get aggregated TF for a person.

        :param person_id: dict with TFs.
        :return:
        """
        doc_ids = self.__elastic.search(person_id, self.CONTENT_FIELD, num=10000).keys()

        tf_agg = {}
        for doc_id in doc_ids:
            tv = self.__elastic.get_termvector(doc_id, self.CONTENT_FIELD)  # , term_stats=True)
            for t, val in tv.items():
                tf_agg[t] = tf_agg.get(t, 0) + val["term_freq"]
        return tf_agg, len(doc_ids)

    def generate_features(self, kb_file, output_file):
        """Core function for generating into output_file the features, with person-item data from kb_file.

        :param kb_file: path to the file with person items (a '.kb'-extension file).
        :param output_file:
        :return:
        """
        feat_w2v_approx = FeaturesW2VSimApprox()

        with open(output_file, "w") as f_out:
            # write tsv header
            header = ["person_id", "prof_id"]
            for k in self.K_VALUES:
                header.append("simCos_w2v_" + str(k))
            f_out.write("\t".join(header) + "\n")

            for line in FileUtils.read_file_as_list(kb_file):
                person_id, prof_id = line.split("\t")  # strip() done in read_file_as_list()
                values = [person_id, prof_id]

                person_tf, num_sent = self.get_person_tf(person_id)

                for k in self.K_VALUES:
                    # we take top-K profession terms

                    # compute simCosK
                    # where K is the top-K terms for the profession
                    term_weights_pr = {}  # dict from top-K profession terms to their tfidf weights
                    term_weights_pe = {}  # dict from top-K person terms to their tfidf weights

                    if prof_id in self.__stats:
                        for term, s in self.__stats[prof_id].items():
                            if s["rank"] <= k:
                                term_weights_pr[term] = float(s["tfidf"])
                                idf = s["tfidf"] / s["tf"]  # we back-generate IDF from profession's TF-IDF
                                term_weights_pe[term] = person_tf.get(term, 0) * idf

                        vec_pr = feat_w2v_approx.get_vector(term_weights_pr)
                        vec_pe = feat_w2v_approx.get_vector(term_weights_pe)
                        cos = cos_sim(vec_pr, vec_pe)
                    else:
                        cos = 0  # in some exceptional cases the profession does not have any sentences
                    values.append(str(cos))

                f_out.write("\t".join(values) + "\n")


def main():
    fts = FeaturesW2VSim()
    fts.load_termstats(TF_IDF_F)
    fts.generate_features(PROFESSION_TRANSLATIONS_F, PROF_W2V_AGGR_COS_SIM_F)


if __name__ == "__main__":
    main()
