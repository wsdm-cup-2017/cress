"""Implements the to-id mappings from persons and from items.

@author: Dario Garigliotti
"""

import os

from nordlys.core.utils.file_utils import FileUtils
from nordlys.core.wsdmcup_2017.config import *


def make_persons_fb_ids(persons_fpath):
    """Our person ID is the Freebase ID where the prefix 'm.' is replaced with 'fb_'.

    :param persons_fpath: 'persons'-named file path.
    """
    with open(PERSONS_IDS_F, "w") as f_out:
        for line in FileUtils.read_file_as_list(persons_fpath):
            person, raw_fb_id = line.split("\t", maxsplit=1)
            fb_id = "fb_" + raw_fb_id[2:]
            f_out.write("{}\t{}\n".format(person, fb_id))


def make_relation_item_ids(rel_items_fpath):
    """Our relation ID is the original relation where the prefix any dash or blank is replaced with underscore.

    :param rel_items_fpath: items file path.
    """
    basename = os.path.basename(rel_items_fpath)  # professions or nationalities

    with open(os.sep.join([DATA_DIR, "{}_ids.tsv".format(basename)]), "w") as f_out:
        for item in FileUtils.read_file_as_list(rel_items_fpath):
            id = item.lower().replace(" ", "_").replace("-", "_")
            f_out.write("{}\t{}\n".format(item, id))


def make_professions_kb_translation(dest_translation_fpath, persons_ids_fpath, professions_ids_fpath,
                                    person_items_fpath):
    """A person ID -to- item ID translation schema is convenient.

    :param dest_translation_fpath: destination file path of IDs translation.
    :param persons_ids_fpath: person IDs file path.
    :param professions_ids_fpath: profession IDs file path.
    :param person_items_fpath: path to the file with person items (a '.kb'-extension file).
    :return:
    """
    persons_ids = {}
    for line in FileUtils.read_file_as_list(persons_ids_fpath):
        person, id = line.split("\t", maxsplit=1)
        persons_ids[person] = id

    professions_ids = {}
    for line in FileUtils.read_file_as_list(professions_ids_fpath):
        prof, id = line.split("\t", maxsplit=1)
        professions_ids[prof] = id

    person_items = {}
    for line in FileUtils.read_file_as_list(person_items_fpath):
        person, item = line.split("\t", maxsplit=1)
        person_items.get(person, []).append(item)

    translations = {}
    for person, items in person_items.items():
        if person not in persons_ids:
            continue
        person_id = persons_ids[person]
        items_ids = []
        for item in items:
            if item not in professions_ids:
                continue
            items_ids.append(professions_ids[item])

        translations[person_id] = items_ids

    with open(dest_translation_fpath, "w") as f_out:
        for person_id, items_ids in translations.items():
            for item_id in items_ids:
                f_out.write("{}\t{}\n".format(person_id, item_id))


def main():
    # OK Done :)
    # persons_fpath = os.sep.join([DATA_DIR, "collection", "persons"])
    # make_persons_fb_ids(persons_fpath)

    # OK Done :)
    # rel_items_fpath = os.sep.join([DATA_DIR, "collection", "professions"])
    # rel_items_fpath = os.sep.join([DATA_DIR, "collection", "nationalities"])
    # make_relation_item_ids(rel_items_fpath)

    # OK Done :)
    # make_professions_kb_translation(PROFESSION_TRANSLATIONS_F, PERSONS_IDS_F, PROFESSIONS_IDS_F, PROF_KB_F)

    pass


if __name__ == '__main__':
    main()
