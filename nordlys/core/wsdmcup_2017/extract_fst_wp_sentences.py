"""Extracts first Wikipedia sentences and paragraphs for a file of listed persons.

@author: Dario Garigliotti
"""

import os.path as ospath
import argparse

from nordlys.core.utils.file_utils import FileUtils

DEST_SENTENCES_K = "dest_sentences_file"
DEST_PARAGRAPHS_K = "dest_paragraphs_file"
SRC_PERSONS_K = "src_persons_file"
SRC_SENTENCES_K = "src_sentences_file"
SRC_PARAGRAPHS_K = "src_paragraphs_file"
ALL_REQUIRED_CONFIG_KS = {DEST_SENTENCES_K, DEST_PARAGRAPHS_K, SRC_PERSONS_K, SRC_SENTENCES_K, SRC_PARAGRAPHS_K}

DBPEDIA_URI_PREFIX = "http://dbpedia.org/resource/"
FREEBASE_URI_PREFIX = "http://rdf.freebase.com/ns/"

FREEBASE_ID_K = "freebaseID"
PERSONS_SENTENCE_K = "1st_sentence"
PERSONS_PARAGRAPH_K = "1st_paragraph"


def obtain_and_dump_person_descriptions(dest_descriptions_file, src_descriptions_file, person_uris):
    """Processes any DBpedia dataset which maps any entity to its description (e.g.: abstract, or comment).
    I.e., generalize both sentence and paragraph extractions for all persons in the person_uris argument.

    :param dest_descriptions_file: file where to dump entity-to-description
    :param src_descriptions_file: DBpedia dataset file (e.g.: short abstracts, or long abstracts)
    :param person_uris: a set of DBpedia URIs where a given entity from DBpedia dataset must belong to,
    in order to be extracted.
    :return:
    """

    # better to write as soon as possible (i.e. both files open),
    # than hold in memory an auxiliary large dict alongside the very large DBpedia dataset
    with FileUtils.open_file_by_type(dest_descriptions_file, mode="w") as f_sentences:
        found_persons = set()  # early stopping flag
        # Iterate only once through all sentences, and collect each of the ones which we need
        for line in FileUtils.read_file_as_list(src_descriptions_file):
            line = line.decode("utf-8", "ignore")  # as we read from the compressed binary file

            if not line.startswith("<{}".format(DBPEDIA_URI_PREFIX)):
                continue

            entity, _, description = line.strip().split(maxsplit=2)  # only split by the first 2 blanks
            # clean up description, by removing language trailer, and opening and closing quote chars
            description = description.split("@en .")[0][1:][:-1]
            if entity not in person_uris:
                continue

            # found a required person
            f_sentences.write("{}\t{}\n".format(entity, description))

            found_persons.add(entity)
            if len(found_persons) >= len(person_uris):
                break

    # not all person URIs appear in the short (or long) abstracts file
    not_found = person_uris.difference(found_persons)
    with FileUtils.open_file_by_type("./persons_without_{}".format(dest_descriptions_file[-9:]), "w") as f_not:
        for person in not_found:
            f_not.write("{}\n".format(person))


def extract_fst_wp_sentences(config):
    """Extracts 1st Wikipedia sentence and paragraphs for a file of listing persons.

    :param config: a configuration dict, or the path to its JSON file.
    :return:
    """
    config = FileUtils.load_config(config)
    assert len(ALL_REQUIRED_CONFIG_KS.difference(set(config.keys()))) == 0  # all required keys are in config

    person_uris = set()
    for person_line in FileUtils.read_file_as_list(config[SRC_PERSONS_K]):
        name, fb_id = person_line.strip().split("\t", maxsplit=1)
        dbpedia_uri = "<{}{}>".format(DBPEDIA_URI_PREFIX, name.replace(" ", "_"))
        person_uris.add(dbpedia_uri)
    print("Loading persons file... OK.")

    obtain_and_dump_person_descriptions(config[DEST_SENTENCES_K], config[SRC_SENTENCES_K], person_uris)
    print("Obtaining 1st Wikipedia sentence for all persons... OK.")

    obtain_and_dump_person_descriptions(config[DEST_PARAGRAPHS_K], config[SRC_PARAGRAPHS_K], person_uris)
    print("Obtaining 1st Wikipedia paragraph for all persons... OK.")

    pass


def main(args):
    if args.fst_wp_sentences_config:
        config = args.fst_wp_sentences_config.strip()

        if not ospath.isfile(config):
            print("invalid path to config file: ", config)
            exit(1)

        print("OK - Config path: {}".format(config))
        extract_fst_wp_sentences(config)


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("fst_wp_sentences_config", help="Path to the config file", type=str)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main(arg_parser())

