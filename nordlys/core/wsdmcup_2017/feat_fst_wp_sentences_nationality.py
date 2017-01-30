"""Implements features about 1st Wikipedia sentences.

@author: Shuo Zhang
"""

import os
import re
import json

import pprint

from nordlys.core.utils.file_utils import FileUtils
from nordlys.core.wsdmcup_2017.config import *
from nordlys.core.wsdmcup_2017.wsdmcup_ids import WSDMCupIDs

OUTPUT_DIR = os.path.expanduser("features")


def main(all_items_fpath, first_snippets_fpath, person_items_fpath, relation):
    """Extracts features about 1st Wikipedia sentences and paragraphs.

        :param all_items_fpath: path to the file with all items (e.g. 'nationality' named file).
        :param first_snippets_fpath:path to the file with first snippets.
        :param person_items_fpath: path to the file with person items (a '.kb'-extension file).
        :param relation: a string in {REL_PROFESSION, REL_NATIONALITY}.
        :return:
        """
    snippet_basename = os.path.basename(first_snippets_fpath).split(".txt")[0]  # for creating dump filename
    print("-" * 79)
    print("Processing for {}".format(snippet_basename))

    # Load all items, e.g. all nationalities(Noun)
    noun = []
    adj = []
    with open(all_items_fpath, "r") as f:
        for line in f:
            Noun, Adj = line.strip().rsplit("\t", 1)
            print("N", Noun, "A", Adj)
            noun.append(Noun)
            adj.append(Adj)
    if "American" in adj:
        print("American inside")

    # Load person-to-snippet mapping
    persons_snippets = {}
    for line in FileUtils.read_file_as_list(first_snippets_fpath):
        person, snippet = line.split("\t")
        person = person.split("<{}".format(DBPEDIA_URI_PREFIX))[-1].split(">")[0].replace("_", " ")
        persons_snippets[person] = snippet

    print("\t Loaded snippets... OK.")
    person_to_all_snippet_items_adj = {}
    for person, snippet in persons_snippets.items():
        # print(snippet)
        for item in adj:
            # important to lowercase when searching for item
            match = re.search(r"[,\s\.]({})[,\s\.]".format(item.lower()), snippet.lower())
            if match:
                if person not in person_to_all_snippet_items_adj.keys():
                    person_to_all_snippet_items_adj[person] = []
                    person_to_all_snippet_items_adj[person].append(item)
                else:
                    person_to_all_snippet_items_adj[person].append(item)

    print("\t Made 1st dict... OK.")

    # Make dict: person to set of (all possible) items in snippet
    person_to_all_snippet_items_noun = {}
    for person, snippet in persons_snippets.items():
        for item in noun:
            # important to lowercase when searching for item
            match = re.search(r"[,\s\.]({})[,\s\.]".format(item.lower()), snippet.lower())
            if match:
                if person not in person_to_all_snippet_items_noun.keys():
                    person_to_all_snippet_items_noun[person] = []
                    person_to_all_snippet_items_noun[person].append(item)
                else:
                    person_to_all_snippet_items_noun[person].append(item)

    # Make dict: person to first item in snippet (among all possible items)
    person_to_first_snippet_item_noun = {}
    for person, snippet in persons_snippets.items():
        fst_item_index = len(snippet) - 1
        fst_item = ""
        for item in person_to_all_snippet_items_noun.get(person, []):
            # in this case, we use re.search() since we need the string index where the found occurrence starts
            # important to lowercase when searching for item
            match = re.search(r"[,\s\.]({})[,\s\.]".format(item.lower()), snippet.lower())
            if match:
                # item (e.g. profession) occurs not only as substring, but all its words (sometimes it's multiword)
                # appear as words in snippet
                # otherwise, it will count "orator" as a profession when it's only a substring of "oratorio"
                item_index = match.start(1)
                if item_index < fst_item_index:
                    fst_item_index = item_index
                    fst_item = item

        person_to_first_snippet_item_noun[person] = fst_item
    print("\t Made 2nd dict... OK.")

    # Make dict: person to first item in snippet (among all possible items)
    person_to_first_snippet_item_adj = {}
    for person, snippet in persons_snippets.items():
        fst_item_index = len(snippet) - 1
        fst_item = ""
        for item in person_to_all_snippet_items_adj.get(person, []):
            # in this case, we use re.search() since we need the string index where the found occurrence starts
            # important to lowercase when searching for item
            match = re.search(r"[,\s\.]({})[,\s\.]".format(item.lower()), snippet.lower())
            if match:
                # item (e.g. profession) occurs not only as substring, but all its words (sometimes it's multiword)
                # appear as words in snippet
                # otherwise, it will count "orator" as a profession when it's only a substring of "oratorio"
                item_index = match.start(1)
                if item_index < fst_item_index:
                    fst_item_index = item_index
                    fst_item = item

        person_to_first_snippet_item_adj[person] = fst_item
    print("\t Made 2nd dict... OK.")

    # Make final feature mappings
    is_item_in_noun = {}  # e.g. person-to-profession-to-yes_or_no mapping
    is_1st_item_in_noun = {}  # e.g. person-to-profession-to-yes_or_no mapping
    for line in FileUtils.read_file_as_list(person_items_fpath):
        person, _, _, item, _ = line.strip().split("\t")

        if person not in is_item_in_noun:
            is_item_in_noun[person] = {}
        feat_value = "1" if item in person_to_all_snippet_items_noun.get(person, []) else "0"
        is_item_in_noun[person][item] = feat_value

        if person not in is_1st_item_in_noun:
            is_1st_item_in_noun[person] = {}
        feat_value = "1" if item in person_to_first_snippet_item_noun.get(person, []) else "0"
        is_1st_item_in_noun[person][item] = feat_value

    print("\t Main for was ran... OK.")

    # Make final feature mappings
    is_item_in_adj = {}  # e.g. person-to-profession-to-yes_or_no mapping
    is_1st_item_in_adj = {}  # e.g. person-to-profession-to-yes_or_no mapping
    for line in FileUtils.read_file_as_list(person_items_fpath):
        person, _, _, nat, item = line.strip().split("\t")

        if person not in is_item_in_adj:
            is_item_in_adj[person] = {}
        feat_value = "1" if item in person_to_all_snippet_items_adj.get(person, []) else "0"
        is_item_in_adj[person][nat] = feat_value

        if person not in is_1st_item_in_adj:
            is_1st_item_in_adj[person] = {}
        feat_value = "1" if item in person_to_first_snippet_item_adj.get(person, []) else "0"
        is_1st_item_in_adj[person][nat] = feat_value

    print("\t Main for was ran... OK.")

    # -------
    # Dumping tsv

    persons_snippets.clear()
    wcup_ids = WSDMCupIDs()

    with open(os.sep.join([OUTPUT_DIR,
                           "is_{}_in_{}_Noun.tsv".format(relation, snippet_basename)]), "w") as f_is_item_in:
        f_is_item_in.write("person\t{}\tis_{}_in_{}_noun\n".format(relation, relation, snippet_basename))
        for person, item_val in sorted(is_item_in_noun.items()):
            for item, val in sorted(item_val.items()):
                f_is_item_in.write("{}\t{}\t{}\n".format(wcup_ids.get_id_from_person(person),
                                                         wcup_ids.get_id_from_nation(item), val))
    with open(os.sep.join([OUTPUT_DIR,
                           "is_1st_{}_in_{}_Noun.tsv".format(relation, snippet_basename)]), "w") as f_is_item_in:
        f_is_item_in.write("person\t{}\tis_the_1st_{}_in_{}_noun\n".format(relation, relation, snippet_basename))
        for person, item_val in sorted(is_1st_item_in_noun.items()):
            for item, val in sorted(item_val.items()):
                f_is_item_in.write("{}\t{}\t{}\n".format(wcup_ids.get_id_from_person(person),
                                                         wcup_ids.get_id_from_nation(item), val))

    with open(os.sep.join([OUTPUT_DIR,
                           "is_{}_in_{}_Adj.tsv".format(relation, snippet_basename)]), "w") as f_is_item_in:
        f_is_item_in.write("person\t{}\tis_{}_in_{}_adj\n".format(relation, relation, snippet_basename))
        for person, item_val in sorted(is_item_in_adj.items()):
            for item, val in sorted(item_val.items()):
                f_is_item_in.write("{}\t{}\t{}\n".format(wcup_ids.get_id_from_person(person),
                                                         wcup_ids.get_id_from_nation(item), val))
    with open(os.sep.join([OUTPUT_DIR,
                           "is_1st_{}_in_{}_Adj.tsv".format(relation, snippet_basename)]), "w") as f_is_item_in:
        f_is_item_in.write("person\t{}\tis_the_1st_{}_in_{}_adj\n".format(relation, relation, snippet_basename))
        for person, item_val in sorted(is_1st_item_in_adj.items()):
            for item, val in sorted(item_val.items()):
                f_is_item_in.write("{}\t{}\t{}\n".format(wcup_ids.get_id_from_person(person),
                                                         wcup_ids.get_id_from_nation(item), val))

    print("\t Dumping both tsv files... OK.")


if __name__ == '__main__':
    relation = REL_NATIONALITY
    all_items_fpath = "nationality_adjectives.tsv"
    person_items_fpath = "nationality_translations.kb"
    # -------
    for first_snippets_fpath in [FIRST_WP_ST_F, FIRST_WP_PG_F]:
        main(all_items_fpath, first_snippets_fpath, person_items_fpath, relation)
    pass
