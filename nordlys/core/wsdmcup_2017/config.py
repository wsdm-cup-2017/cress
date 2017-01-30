"""
wsdmcup-2017 package-specific configurations.

@author: Dario Garigliotti
"""

from os import sep

# ------------------------------------------------
# Constants

# -----------
# Some data
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

# -----------
#  Relations in competition
REL_PROFESSION = "profession"
REL_NATIONALITY = "nationality"
VALID_RELS = [REL_PROFESSION, REL_NATIONALITY]

# -----------
#  Main data paths

# Dirs
WSDM_DIR = "/path/to/files"
COLLECTION_DIR = sep.join([WSDM_DIR, "collection"])
FIRST_WP_ST_DIR = sep.join([WSDM_DIR, "first_wp_sentences"])
DATA_DIR = sep.join([WSDM_DIR, "data"])
FEATURES_DIR = sep.join([DATA_DIR, "features"])
# Files
WP_ST_F = sep.join([COLLECTION_DIR, "wiki-sentences"])
PERSONS_F = sep.join([COLLECTION_DIR, "persons"])
PROFESSIONS_F = sep.join([COLLECTION_DIR, "professions"])
NATIONALITIES_F = sep.join([COLLECTION_DIR, "nationalities"])
#
PROF_KB_F = sep.join([COLLECTION_DIR, REL_PROFESSION + ".kb"])
NAT_KB_F = sep.join([COLLECTION_DIR, REL_NATIONALITY + ".kb"])
#
PERSONS_IDS_F = sep.join([DATA_DIR, "persons_ids.tsv"])
PROFESSIONS_IDS_F = sep.join([DATA_DIR, "professions_ids.tsv"])
NATIONALITIES_IDS_F = sep.join([DATA_DIR, "nationalities_ids.tsv"])
PROFESSION_TRANSLATIONS_F = sep.join([DATA_DIR, "profession_translations.kb"])
COUNTRIES_NATIONALITIES_F = sep.join([DATA_DIR, "nationality_adjectives.tsv"])
#
FIRST_WP_ST_F = sep.join([FIRST_WP_ST_DIR, "first_wp_sentences.txt"])  # first WP sentences
FIRST_WP_PG_F = sep.join([FIRST_WP_ST_DIR, "first_wp_paragraphs.txt"])  # first WP paragraphs
#
TF_IDF_F = sep.join([DATA_DIR, "tf_idf.tsv"])
#
PROF_APPROX_W2V_AGGR_COS_SIM_F = sep.join([FEATURES_DIR, "profession-approx-w2v_aggr_cos_sim.tsv"])
PROF_W2V_AGGR_COS_SIM_F = sep.join([FEATURES_DIR, "profession_w2v_aggr_cos_sim.tsv"])

# -----------
#  Indices
WP_ST_INDEX = "wsdmcup17_wp_sentences_prof"
WP_ST_INDEX_ID = "wsdmcup17_wp_sentences_prof_id"

# -----------
#  Data items utils
DBPEDIA_URI_PREFIX = "http://dbpedia.org/resource/"
FREEBASE_URI_PREFIX = "http://rdf.freebase.com/ns/"

# -----------
# ML

PROFESSION_TRAIN_F = sep.join([DATA_DIR, REL_PROFESSION + ".train"])
NATIONALITY_TRAIN_F = sep.join([DATA_DIR, REL_NATIONALITY + ".train"])

PROFESSION_INSS_TRAIN = sep.join([DATA_DIR, "profession_train.json"])
NATIONALITY_INSS_TRAIN = sep.join([DATA_DIR, "nationality_train.json"])

PROFESSION_INSS_ALL = sep.join([DATA_DIR, "profession_all.json"])
NATIONALITY_INSS_ALL = sep.join([DATA_DIR, "nationality_all.json"])

PROFESSION_MODEL = sep.join([DATA_DIR, "profession.model"])
NATIONALITY_MODEL = sep.join([DATA_DIR, "nationality.model"])

# -----------
# Miscellaneous

S_COMMA = 'ș'  # https://en.wikipedia.org/wiki/S-comma
S_CEDILLA = 'ş'  # https://en.wikipedia.org/wiki/%C5%9E
