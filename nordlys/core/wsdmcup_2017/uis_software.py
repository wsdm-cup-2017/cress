"""UiS (University of Stavanger) - IAI Group - WSDM Cup 2017 - Main software entry point

@author: Dario Garigliotti
@author: Faegheh Hasibi
"""

import os
import argparse

from nordlys.core.wsdmcup_2017.config import *
from nordlys.core.wsdmcup_2017.triple_scorer import TripleScorer


def arg_parser():
    description_str = "UiS (University of Stavanger) - IAI Group - WSDM Cup 2017 - Main software entry point."

    parser = argparse.ArgumentParser(description=description_str)
    r = parser.add_argument_group("required arguments")
    r.add_argument("-i", "--input",
                   help="2-columns input file (can be specified more than once)",
                   required=True, action="append", type=str)
    r.add_argument("-o", "--output_path", help="Output directory", required=True, type=str)
    args = parser.parse_args()
    return args


def get_relation(input_file):
    """Gets the relation from in the input file.

    :param input_file: input file path.
    """
    stderr_bad_relation = "input file name is not valid"
    print("Input file: {}".format(input_file))
    relation = ""  # for avoiding 'Local variable might be referenced before assignment' warning
    try:
        relation = os.path.basename(input_file).split(".", maxsplit=1)[0]
    except IndexError:
        print(stderr_bad_relation)
        exit(1)
    assert relation in VALID_RELS, stderr_bad_relation
    return relation


def read_input(input_file):
    """Reads the input file and returns a list of (person, item) pairs, where item is a profession or nationality.

    :param input_file: input file path.
    """
    person_items = []
    with open(input_file, "r") as f:
        for line in f:
            cols = line.strip().split("\t")
            person, item = cols[0].strip(), cols[1].strip()
            person_items.append((person, item))
    return person_items


def write_output(input_items, scored_items, output_file):
    """Writes scored items to the output file.

    :param input_items: list [(person, item), ...]
    :param scored_items: dictionary {(person, item): score}
    :param output_file: name of output file
    """
    with open(output_file, "w") as f:
        for person, item in input_items:
            person_replaced = person.replace(S_CEDILLA, S_COMMA).replace(S_CEDILLA.upper(), S_COMMA.upper())
            score = int(round(scored_items[(person_replaced, item)]))
            score = 7 if score > 7 else score
            score = 0 if score < 0 else score
            f.write(person + "\t" + item + "\t" + str(int(round(score))) + "\n")
    print("Output file: " + output_file)


def main(args):
    print(args.input)
    print(args.output_path)

    for input_file in args.input:
        relation = get_relation(input_file)
        input_items = read_input(input_file)
        scorer = TripleScorer(relation)
        # scored_items = scorer.cross_validate()
        # scorer.train()
        scored_items = scorer.score(input_items)
        output_file = os.sep.join([args.output_path, os.path.basename(input_file)])
        write_output(input_items, scored_items, output_file)


if __name__ == '__main__':
    main(arg_parser())
