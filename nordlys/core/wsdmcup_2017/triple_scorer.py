"""Ranks professions

@author: Faegheh Hasibi
"""

import pickle
import sys

from nordlys.core.ml.instances import Instances
from nordlys.core.ml.ml import ML
from nordlys.core.utils.file_utils import FileUtils
from nordlys.core.wsdmcup_2017.config import *
from nordlys.core.wsdmcup_2017.wsdmcup_ids import WSDMCupIDs


class TripleScorer(object):
    def __init__(self, relation, model=None, params=None):
        self.__relation = relation
        self.__train_file = PROFESSION_INSS_TRAIN if relation == REL_PROFESSION else NATIONALITY_INSS_TRAIN
        self.__inss_file = PROFESSION_INSS_ALL if relation == REL_PROFESSION else NATIONALITY_INSS_ALL
        self.__model_file = PROFESSION_MODEL if relation == REL_PROFESSION else NATIONALITY_MODEL
        self.__wsdmcup_ids = WSDMCupIDs()
        self.__ml_config = self.gen_ml_config(relation, model, params)

    @staticmethod
    def gen_ml_config(relation, model=None, params=None):
        default_params = {"tree": 1000, "maxfeat": 5} if relation == REL_PROFESSION else {"tree": 1000, "maxfeat": 2}
        config = {"category": "regression",
                  "model": model if model else "rf",
                  "parameters": params if params else default_params
                  }
        return config

    def __inss2items(self, inss):
        """Converts instances to a list of (person, item, score) triples."""
        scored_items = {}
        for ins in inss.get_all():
            person = self.__wsdmcup_ids.get_person_from_id(ins.get_property("person"))
            item_id = ins.get_property(self.__relation)
            if self.__relation == REL_PROFESSION:
                item = self.__wsdmcup_ids.get_prof_from_id(item_id)
            else:
                item = self.__wsdmcup_ids.get_nation_from_id(item_id)
            score = ins.score
            scored_items[(person, item)] = score
        return scored_items

    def __items2inss(self, person_items):
        """Converts (person, item) tuples to instances."""
        all_inss = Instances.from_json(self.__inss_file)
        print("Converting items to instances ...")
        inss = Instances()
        for person, item in person_items:
            person_id = self.__wsdmcup_ids.get_id_from_person(person)
            if self.__relation == REL_PROFESSION:
                item_id = self.__wsdmcup_ids.get_id_from_prof(item)
            else:
                item_id = self.__wsdmcup_ids.get_id_from_nation(item)
            ins_id = person_id + "_" + item_id
            ins = all_inss.get_instance(ins_id)
            if ins is None:
                print(person, item, "not found!")
            inss.add_instance(ins)
        return inss

    def train(self):
        """Trains the model."""
        self.__ml_config["save_model"] = self.__model_file

        ml = ML(self.__ml_config)
        ins_train = Instances.from_json(self.__train_file)
        ml.train_model(ins_train)
        # inss = ml.apply_model(ins_train, model)
        # return self.__inss2triples(inss)

    def cross_validate(self):
        """Performs cross validation on train instances and returns list of ranked items"""
        self.__ml_config["cross_validation"] = {
            "create_splits": True,
            "splits_file": DATA_DIR + "/splits.json",
            "k": 5,
            "split_strategy": "person"
        }
        self.__ml_config["training_set"] = self.__train_file
        inss = ML(self.__ml_config).run()
        return self.__inss2items(inss)

    def score(self, items):
        inss = self.__items2inss(items)
        print("Loading model ...")
        model = pickle.load(open(self.__model_file, "rb"))
        inss = ML(self.__ml_config).apply_model(inss, model)
        return self.__inss2items(inss)


def main(config):
    ml = ML(FileUtils.load_config(config))
    inss = ml.run()


if __name__ == "__main__":
    main(sys.argv[1:])
