"""Aggregates features

@author: Faegheh Hasibi
"""

import argparse
import csv
import json

from nordlys.core.wsdmcup_2017.config import *
from nordlys.core.wsdmcup_2017.wsdmcup_ids import WSDMCupIDs


class AggFeat(object):
    def __init__(self, relation):
        self.__relation = relation
        self.__train_file = PROFESSION_TRAIN_F if relation == REL_PROFESSION else NATIONALITY_TRAIN_F

    def load_train_labels(self):
        """Creates the target label dictionary: {person_prof: label}"""
        wsdm_ids = WSDMCupIDs()
        target_labels = {}
        with open(self.__train_file, "r") as f:
            for line in f:
                cols = line.strip().split("\t")
                person_id = wsdm_ids.get_id_from_person(cols[0])
                if self.__relation == REL_PROFESSION:
                    item_id = wsdm_ids.get_id_from_prof(cols[1])
                else:
                    item_id = wsdm_ids.get_id_from_nation(cols[1])
                ins_id = person_id + "_" + item_id
                target_labels[ins_id] = cols[2]
        return target_labels

    def load_file(self, file_name):
        """Reads a feature file and generates json format of instances."""
        print("Loading file [" + file_name + "] ...")
        instances = {}
        with open(file_name, "r") as tsvfile:
            f = csv.DictReader(tsvfile, delimiter="\t", quoting=csv.QUOTE_NONE)
            for line in f:
                ins_id = line["person"] + "_" + line[self.__relation]
                properties = {"person": line["person"], self.__relation: line[self.__relation]}
                features = {}
                for key, val in line.items():
                    if (key != "person") and (key != self.__relation):
                        features[key] = val
                instances[ins_id] = {"properties": properties, "features": features}
        return instances

    def merge_features(self, feature_files):
        """Merges features from all feature files"""
        print("Merging all features ...")
        merged_inss = {}
        for file in feature_files:
            instances = self.load_file(file)
            for ins_id, ins in instances.items():
                if ins_id not in merged_inss:
                    merged_inss[ins_id] = ins
                else:
                    merged_inss[ins_id]["features"].update(ins["features"])
                merged_inss.get(ins_id, {}).get("features", {}).update(ins["features"])
        return merged_inss

    def gen_train_inss(self, merged_inss):
        """Generates instances in the train file."""
        print("Generating train instances ...")
        # todo: test with actual files
        train_lables = self.load_train_labels()
        train_inss = {}
        for ins_id, target in train_lables.items():
            if ins_id in merged_inss:
                train_inss[ins_id] = merged_inss[ins_id]
                train_inss[ins_id]["target"] = target
            else:
                print("WARNING: instance id " + ins_id + "does not exists!")
        return train_inss


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--train", help="creates train instances", action="store_true", default=False)
    parser.add_argument("-f", "--feature_files", help="run files, separated with space", nargs="+")
    parser.add_argument("-r", "--relation", help="output file", type=str)
    args = parser.parse_args()
    return args


def set_feature_files(relation):
    if relation == "profession":
        feature_files = [FEATURES_DIR + "/is_1st_profession_in_first_wp_paragraphs.tsv",
                         FEATURES_DIR + "/is_1st_profession_in_first_wp_sentences.tsv",
                         FEATURES_DIR + "/is_profession_in_first_wp_paragraphs.tsv",
                         FEATURES_DIR + "/is_profession_in_first_wp_sentences.tsv",
                         FEATURES_DIR + "/profession_termstats.tsv"]
    else:
        feature_files = [FEATURES_DIR + "/is_1st_nationality_in_first_wp_paragraphs_Adj.tsv",
                         FEATURES_DIR + "/is_1st_nationality_in_first_wp_paragraphs_Noun.tsv",
                         FEATURES_DIR + "/is_1st_nationality_in_first_wp_sentences_Adj.tsv",
                         FEATURES_DIR + "/is_1st_nationality_in_first_wp_sentences_Noun.tsv",
                         FEATURES_DIR + "/is_nationality_in_first_wp_paragraphs_Adj.tsv",
                         FEATURES_DIR + "/is_nationality_in_first_wp_paragraphs_Noun.tsv",
                         FEATURES_DIR + "/is_nationality_in_first_wp_sentences_Adj.tsv",
                         FEATURES_DIR + "/is_nationality_in_first_wp_sentences_Noun.tsv",
                         FEATURES_DIR + "/nat_features_freq_Adj.tsv",
                         FEATURES_DIR + "/nat_features_freq_Noun.tsv"]
    return feature_files


def main(args):
    if args.feature_files is None:
        args.feature_files = set_feature_files(args.relation)
    merger = AggFeat(args.relation)
    merged_inss = merger.merge_features(args.feature_files)
    if args.train:
        train_inss = merger.gen_train_inss(merged_inss)
        output_file = PROFESSION_INSS_TRAIN if args.relation == REL_PROFESSION else NATIONALITY_INSS_TRAIN
        json.dump(train_inss, open(output_file, "w"), indent=4, sort_keys=True)
    else:
        output_file = PROFESSION_INSS_ALL if args.relation == REL_PROFESSION else NATIONALITY_INSS_ALL
        json.dump(merged_inss, open(output_file, "w"), indent=4, sort_keys=True)
    print("Output file:", output_file)


if __name__ == "__main__":
    main(arg_parser())
