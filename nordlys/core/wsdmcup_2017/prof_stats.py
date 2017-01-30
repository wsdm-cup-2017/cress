"""Generates profession statisctics

@author: Shuo Zhang
@author: Faegheh Hasibi
"""

import argparse
import math
from nordlys.core.retrieval.elastic_cache import ElasticCache
from nordlys.core.wsdmcup_2017.config import WP_ST_INDEX_ID, PROFESSIONS_F


class ProfStats():
    CONTENT_FIELD = "content"
    PROF_FIELD = "professions"
    K = 30000  # keep top-K profession terms

    def __init__(self, index_name=WP_ST_INDEX_ID):
        self.__elastic = ElasticCache(index_name)

    def gen_stats(self, prof, output_file):
        """Writes the stats into the file."""
        print("\tgetting term frequencies ...")
        tf, df = self.get_tf_agg(prof)
        # print("\tgetting document frequencies ... (", len(tf.keys()), "terms)")
        # df2 = self.get_df(tf.keys())
        print("\tcomputing tf-idf ...")
        tf_idf = self.compute_tf_idf(tf, df)

        out_str = ""
        i = 0
        for t, tfidf in sorted(tf_idf.items(), key=lambda x: x[1], reverse=True):
            out_str += prof + "\t" + t + "\t" + str(tf[t]) + "\t" + str(df[t]) + "\t" + str(tfidf) + "\n"
            i += 1
            if i == self.K:  # Only print top-k terms
                break
        open(output_file, "a").write(out_str)
        return

    def compute_tf_idf(self, tf, df):
        """Computes tf.idf = (tf/doc_len) * (log n(docs)/df)

        :param tf: dictionary of tf for all terms
        :param df: dictionary of df for all terms
        :return: dictionary of tf.idf scores
        """
        tf_idf = {}
        prof_doc_len = sum(tf.values())
        for t in tf.keys():
            normalized_tf = tf[t] / prof_doc_len
            n_docs = self.__elastic.num_docs()
            idf = math.log(n_docs / df[t])
            tf_idf[t] = normalized_tf * idf
        return tf_idf

    def get_df(self, terms):
        """Returns document frequency for all terms."""
        df = {}
        for t in terms:
            df[t] = self.__elastic.doc_freq(t, field=self.CONTENT_FIELD)
        return df

    def get_tf_agg(self, prof):
        """Given a list of ids to get all their tf_idf in a dictionary."""
        size = 1000
        tf_agg = {}
        df = {}
        # doc_ids = self.__elastic.search(prof, self.PROF_FIELD, num=size).keys()
        doc_ids = self.__elastic.search_scroll(prof, field=self.PROF_FIELD, num=size).keys()
        print(len(doc_ids), "sentences")
        for i, doc_id in enumerate(doc_ids):
            tv = self.__elastic.get_termvector(doc_id, self.CONTENT_FIELD, term_stats=True)
            for t, val in tv.items():
                tf_agg[t] = tf_agg.get(t, 0) + val["term_freq"]
                if t not in df:
                    df[t] = val["doc_freq"]
        return tf_agg, df


def get_profs(prof_file):
    """Returns list of all the professions.
    All the professions are converted to the format stored in the index.
    """
    profs = []
    with open(prof_file, "r") as f:
        for line in f:
            prof = line.strip().lower().replace(" ", "_")
            profs.append(prof)
    return profs


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--k", help="top-k temrs to be stored for each profession", type=int, default=0)
    parser.add_argument("-o", "--output_file", help="output file", type=str, required=True)
    parser.add_argument("-p", "--profession_id", help="profession id to start from", type=int)
    args = parser.parse_args()
    return args


def main(args):
    open(args.output_file, "w").write("")

    prof_stats = ProfStats()
    profs = get_profs(PROFESSIONS_F)
    for i in range(args.k, len(profs)):
        print("Computing stats for " + str(i + 1) + "th profession: [" + profs[i] + "] ...")
        prof_stats.gen_stats(profs[i], args.output_file)


if __name__ == "__main__":
    main(arg_parser())
