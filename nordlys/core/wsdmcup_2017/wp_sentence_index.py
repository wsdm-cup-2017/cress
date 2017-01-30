"""
Wikipedia sentence indexer
-------------------------

Index wikipedia sentences in http://broccoli.cs.uni-freiburg.de/wsdm-cup-2017/wiki-sentences

@author: Shuo Zhang
"""

from collections import defaultdict

from nordlys.core.retrieval.elastic import Elastic
from nordlys.core.wsdmcup_2017.config import WP_ST_INDEX_ID, PROF_KB_F, WP_ST_F
from bs4 import BeautifulSoup
from urllib.request import urlopen
from nordlys.core.wsdmcup_2017.wsdmcup_ids import WSDMCupIDs
import re


def gen_mappings():
    """Creates json file containing profession as key and values as the list of names."""
    mappings = defaultdict(list)
    with open(PROF_KB_F, "r") as f:
        for line in f:
            cols = line.strip().split("\t")
            person, prof = cols[0], cols[1]
            mappings[person].append(prof)
    return mappings


def index(mapper, bulk_size=10000):
    """Indexing"""
    pres_prof_mapping = gen_mappings()
    file = open(WP_ST_F, "r")
    index_name = WP_ST_INDEX_ID
    mappings = {
        "content": Elastic.analyzed_field(),
        "professions": Elastic.notanalyzed_field()
    }
    elastic = Elastic(index_name)
    elastic.create_index(mappings, force=True)
    doc_id = 0
    docs = {}
    for line in file:
        doc_id += 1
        profs = []
        while ("[" in line):  # replace [A|B] with A
            matchObj = re.search('\[(.*?)\]', line)
            entity = matchObj.group(1).split("|")[0]
            name = entity.replace("_", " ")
            entity_id = mapper.get_id_from_person(name)
            prof_list = pres_prof_mapping[name]
            prof_list = [mapper.get_id_from_prof(prof) for prof in prof_list]
            profs += prof_list
            line = line.replace("[" + matchObj.group(1) + "]", entity_id)
        docs[doc_id] = {"content": line, "professions": list(set(profs))}
        if len(docs) == bulk_size:  # bulk add 10000 sentences into elastic
            elastic.add_docs_bulk(docs)
            docs = {}
            print(doc_id / 1000, "K documents indexed.")

    # if len(docs) < 10000: # index the last butch of sentences
    elastic.add_docs_bulk(docs)


if __name__ == "__main__":
    mapper = WSDMCupIDs()
    index(mapper)
