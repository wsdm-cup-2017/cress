"""
Generating features related to term statistics

@author Krisztian Balog
@author Shuo Zhang
"""

from nordlys.core.retrieval.elastic_cache import ElasticCache
from nordlys.core.utils.file_utils import FileUtils
from math import sqrt

from nordlys.core.wsdmcup_2017.config import WP_ST_INDEX_ID


def square_rooted_sum(v):
    return sqrt(sum([a * a for a in v]))


def cos_sim(v1, v2):
    numerator = sum(a * b for a, b in zip(v1, v2))
    denominator = square_rooted_sum(v1) * square_rooted_sum(v2)
    res = numerator / denominator if denominator != 0 else 0
    return res


class FeaturesTermStats():
    CONTENT_FIELD = "content"
    PROF_FIELD = "professions"
    K_VALUES = [10, 50, 100, 200, 500, 1000]
    STOPWORDS = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself",
                 "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself",
                 "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that",
                 "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
                 "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as",
                 "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through",
                 "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off",
                 "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how",
                 "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not",
                 "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should",
                 "now"]
    MAX_K = max(K_VALUES)

    def __init__(self, index_name=WP_ST_INDEX_ID):
        self.__elastic = ElasticCache(index_name)
        self.__stats = None

    def load_termstats(self, input_file):
        """load term statistics from file"""
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
                if term in self.STOPWORDS:  # filter stopwords
                    continue
                if term.startswith("fb_"):  # filter entity terms
                    continue
                if prof not in self.__stats:
                    self.__stats[prof] = {}
                self.__stats[prof][term] = {"tf": int(tf), "df": int(df), "tfidf": float(tfidf), "rank": rank}

    def get_person_tf(self, person_id):
        """
        Get aggregated TF for a person
        :param person_id: dict with TFs
        :return:
        """
        doc_ids = self.__elastic.search(person_id, self.CONTENT_FIELD, num=10000).keys()
        print(person_id, "with", len(doc_ids), "sentences")
        tf_agg = {}
        for doc_id in doc_ids:
            tv = self.__elastic.get_termvector(doc_id, self.CONTENT_FIELD)  # , term_stats=True)
            for t, val in tv.items():
                tf_agg[t] = tf_agg.get(t, 0) + val["term_freq"]
        return tf_agg, len(doc_ids)

    def generate_features(self, kb_file, output_file):
        """Generating features related to term statistics"""

        fout = open(output_file, "w")

        # write tsv header
        header = ["person", "profession"]
        for k in self.K_VALUES:
            header.append("sumProfTerms_" + str(k))
            header.append("simCos_" + str(k))
        fout.write("\t".join(header) + "\n")

        with FileUtils.open_file_by_type(kb_file) as kb_f:
            for line in kb_f:
                person_id, prof_id = line.strip().split("\t")
                values = [person_id, prof_id]

                person_tf, num_sent = self.get_person_tf(person_id)

                for k in self.K_VALUES:
                    # we take top-K profession terms

                    # Compute sumProfTerms: \sum_{t \in T_k(pr)}\sum_{s \in S(pe)} tf(t,s) w(t,pr)
                    # where w(t,pe )= TFIDF(t,pr) = \frac{\sum_{s \in S(pr)} tf(t,s)}
                    sum_prof_terms = 0
                    for term, tf in person_tf.items():
                        pt = self.__stats.get(prof_id, {}).get(term, {})
                        if pt.get("rank", 100000) > k:  # skip term if not in top-K
                            continue
                        sum_prof_terms += tf * pt.get("tfidf", 0)
                    values.append(str(sum_prof_terms))

                    # compute simCosK
                    # where K is the top-K terms for the profession
                    vec_pr = []  # construct prof vector
                    vec_pe = []  # construct person vector

                    if prof_id in self.__stats:
                        for term, s in self.__stats[prof_id].items():
                            if s["rank"] <= k:
                                vec_pr.append(s["tfidf"])
                                idf = s["tfidf"] / s["tf"]  # we back-generate IDF from profession's TF-IDF
                                vec_pe.append(person_tf.get(term, 0) * idf)
                        cos = cos_sim(vec_pr, vec_pe)
                    else:
                        cos = 0  # in some exceptional cases the profession does not have any sentences
                    values.append(str(cos))

                fout.write("\t".join(values) + "\n")
                print(values)

        fout.close()


def main():
    fts = FeaturesTermStats()
    fts.load_termstats("/data/scratch/wsdm-cup-2017/data/tf_idf.tsv")
    fts.generate_features("/data/scratch/wsdm-cup-2017/data/profession_translations.kb",
                          "/data/scratch/wsdm-cup-2017/data/features_termstats_prof.tsv")


if __name__ == "__main__":
    main()
