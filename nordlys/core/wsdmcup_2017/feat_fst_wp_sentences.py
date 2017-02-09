"""Implements features about 1st Wikipedia sentences.

@author: Dario Garigliotti
"""

import os
import re

from nordlys.core.utils.file_utils import FileUtils
from nordlys.core.wsdmcup_2017.config import *  # we know this module so no danger, but be careful ;)
from nordlys.core.wsdmcup_2017.wsdmcup_ids import WSDMCupIDs

OUTPUT_DIR = os.path.expanduser("~/")


def main(all_items_fpath, first_snippets_fpath, person_items_fpath, relation):
    """Extracts features about 1st Wikipedia sentences and paragraphs.

    :param all_items_fpath: path to the file with all items (e.g. 'professions' named file).
    :param first_snippets_fpath:path to the file with first snippets.
    :param person_items_fpath: path to the file with person items (a '.kb'-extension file).
    :param relation: a string in {REL_PROFESSION, REL_NATIONALITY}.
    :return:
    """

    snippet_basename = os.path.basename(first_snippets_fpath).split(".txt")[0]  # for creating dump filename
    print("Processing for {}".format(snippet_basename))

    # Load all items, e.g. all professions
    all_rel_items = {item for item in FileUtils.read_file_as_list(all_items_fpath)}

    # Load person-to-snippet mapping
    persons_snippets = {}
    for line in FileUtils.read_file_as_list(first_snippets_fpath):
        person, snippet = line.split("\t")
        person = person.split("<{}".format(DBPEDIA_URI_PREFIX))[-1].split(">")[0].replace("_", " ")
        persons_snippets[person] = snippet
    print("\t Loaded snippets... OK.")

    # Make dict: person to set of (all possible) items in snippet
    person_to_all_snippet_items = {}
    # person_counter = 0
    for person, snippet in persons_snippets.items():
        for item in all_rel_items:
            # important to lowercase when searching for item
            match = re.search(r"[,\s\.]({})[,\s\.]".format(item.lower()), snippet)
            if match:
                person_to_all_snippet_items.get(person, set()).add(item)
    print("\t Made 1st dict... OK.")

    # Make dict: person to first item in snippet (among all possible items)
    person_to_first_snippet_item = {}
    # person_counter = 0
    for person, snippet in persons_snippets.items():
        fst_item_index = len(snippet) - 1
        fst_item = ""
        for item in person_to_all_snippet_items.get(person, set()):
            # in this case, we use re.search() since we need the string index where the found occurrence starts
            # important to lowercase when searching for item
            match = re.search(r"[,\s\.]({})[,\s\.]".format(item.lower()), snippet)
            if match:
                # item (e.g. profession) occurs not only as substring, but all its words (sometimes it's multiword)
                # appear as words in snippet
                # otherwise, it will count, e.g., "orator" as a profession when it's only a substring of "oratorio"
                item_index = match.start(1)
                if item_index < fst_item_index:
                    fst_item_index = item_index
                    fst_item = item

        person_to_first_snippet_item[person] = fst_item
    print("\t Made 2nd dict... OK.")

    # Make final feature mappings
    is_item_in = {}  # e.g. person-to-profession-to-yes_or_no mapping
    is_1st_item_in = {}  # e.g. person-to-profession-to-yes_or_no mapping
    for line in FileUtils.read_file_as_list(person_items_fpath):
        person, item = line.split("\t", maxsplit=1)

        if person not in is_item_in:
            is_item_in[person] = {}
        feat_value = "1" if item in person_to_all_snippet_items.get(person, set()) else "0"
        is_item_in[person][item] = feat_value

        if person not in is_1st_item_in:
            is_1st_item_in[person] = {}
        feat_value = "1" if item in person_to_first_snippet_item.get(person, set()) else "0"
        is_1st_item_in[person][item] = feat_value

    print("\t Main for-loop running... OK.")

    # -------
    # Dumping tsv
    persons_snippets.clear()
    wcup_ids = WSDMCupIDs()

    with open(os.sep.join([OUTPUT_DIR,
                           "is_{}_in_{}.tsv".format(relation, snippet_basename)]), "w") as f_is_item_in:
        f_is_item_in.write("person\t{}\tis_{}_in_{}\n".format(relation, relation, snippet_basename))
        for person, item_val in sorted(is_item_in.items()):
            for item, val in sorted(item_val.items()):
                f_is_item_in.write("{}\t{}\t{}\n".format(wcup_ids.get_id_from_person(person),
                                                         wcup_ids.get_id_from_prof(item), val))
    with open(os.sep.join([OUTPUT_DIR,
                           "is_1st_{}_in_{}.tsv".format(relation, snippet_basename)]), "w") as f_is_item_in:
        f_is_item_in.write("person\t{}\tis_the_1st_{}_in_{}\n".format(relation, relation, snippet_basename))
        for person, item_val in sorted(is_1st_item_in.items()):
            for item, val in sorted(item_val.items()):
                f_is_item_in.write("{}\t{}\t{}\n".format(wcup_ids.get_id_from_person(person),
                                                         wcup_ids.get_id_from_prof(item), val))

    print("\t Dumping both tsv files... OK.")


if __name__ == '__main__':
    relation = REL_PROFESSION
    all_items_fpath = PROFESSIONS_F
    person_items_fpath = PROF_KB_F

    for first_snippets_fpath in [FIRST_WP_ST_F, FIRST_WP_PG_F]:
        main(all_items_fpath, first_snippets_fpath, person_items_fpath, relation)
    pass
