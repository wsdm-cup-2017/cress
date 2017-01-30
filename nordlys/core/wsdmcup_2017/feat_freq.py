"""
Generating features of freq-person-nationality

@author Shuo Zhang
"""

from nordlys.core.retrieval.elastic_cache import ElasticCache
from nordlys.core.utils.file_utils import FileUtils
from nordlys.core.wsdmcup_2017.config import WP_ST_INDEX_ID


class FeaturesTermStats():
    CONTENT_FIELD = "content"
    STOPWORDS = [
        "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in",
        "into", "is", "it", "no", "not", "of", "on", "or", "such", "that", "the",
        "their", "then", "there", "these", "they", "this", "to", "was", "will", "with"]

    def __init__(self, index_name=WP_ST_INDEX_ID):
        self.__elastic = ElasticCache(index_name)
        self.__stats = None

    def get_per_nat_tf(self, person_id, nats):
        """
        Compute freqPerNat: \frac{|\{s : pe \in s, nt \in s\}|}{|S(pe)|}
        :param person_id:
        :param nats: nationality+adj, e.g. Germany, German
        :return: freqPerNat
        """

        body = {
            "query": {
                "bool": {
                    "must": {
                        "term": {"content": person_id}
                    }
                }
            }
        }

        doc_ids = self.__elastic.search_complex(body, self.CONTENT_FIELD, num=10000).keys()
        n_s_pe = len(doc_ids)  # number of sentences containing person
        # print(n_s_pe)
        noun = nats[0]
        noun_query = self.__elastic.analyze_query(noun)

        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {"content": person_id}
                        },
                        {
                            "match_phrase": {"content": noun_query}
                        }
                    ]
                }
            }}

        doc_ids_noun = self.__elastic.search_complex(body, self.CONTENT_FIELD, num=10000).keys()
        n_co_noun = len(doc_ids_noun)
        # print("Noun", n_co_noun)
        adj = nats[1]
        adj_query = self.__elastic.analyze_query(adj)

        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {"content": person_id}
                        },
                        {
                            "match_phrase": {"content": adj_query}
                        }
                    ]
                }
            }}
        doc_ids_adj = self.__elastic.search_complex(body, self.CONTENT_FIELD, num=10000).keys()
        n_co_adj = len(doc_ids_adj)
        # print("Adj", n_co_adj)

        if n_s_pe == 0:
            return 0.0, 0.0
        else:
            return n_co_noun / n_s_pe, n_co_adj / n_s_pe

    def generate_features(self, kb_file, output_file1, output_file2):
        """Generate features of freq-person-nationality"""

        fout1 = open(output_file1, "w")
        fout2 = open(output_file2, "w")

        # write tsv header
        header = ["person", "nationality", "freq_person_nationality_noun"]
        fout1.write("\t".join(header) + "\n")
        header = ["person", "nationality", "freq_person_nationality_adj"]
        fout2.write("\t".join(header) + "\n")

        with FileUtils.open_file_by_type(kb_file) as kb_f:
            line_count = 1
            for line in kb_f:
                print(line_count)
                line_count += 1
                person_id, nat_id, noun, adj = line.strip().split("\t")
                values_noun = [person_id, nat_id]
                values_adj = [person_id, nat_id]
                nats = [noun, adj]
                fpn_noun, fpn_adj = self.get_per_nat_tf(person_id, nats)
                values_noun.append(str(fpn_noun))
                values_adj.append(str(fpn_adj))
                fout1.write("\t".join(values_noun) + "\n")
                fout2.write("\t".join(values_adj) + "\n")
        fout1.close()
        fout2.close()


def main():
    fts = FeaturesTermStats()
    fts.generate_features("/data/scratch/wsdm-cup-2017/data/nationality_translations.kb",
                          "/data/scratch/wsdm-cup-2017/data/features/nat_features_freq_Noun2.tsv",
                          "/data/scratch/wsdm-cup-2017/data/features/nat_features_freq_Adj2.tsv")


if __name__ == "__main__":
    main()
