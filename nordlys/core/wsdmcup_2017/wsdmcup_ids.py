"""Implements WSDMCupIDs class for id translations.

@author: Dario Garigliotti
"""

from nordlys.core.utils.file_utils import FileUtils
from nordlys.core.wsdmcup_2017.config import *


class WSDMCupIDs(object):
    """
    Wraps a 2-way dictionary between persons and person IDs, and another 2-way dict between professions and their IDs.
    """

    def __init__(self):
        self.persons_ids = {}
        self.ids_persons = {}
        for line in FileUtils.read_file_as_list(PERSONS_IDS_F):
            person, id = line.split("\t", maxsplit=1)
            self.persons_ids[person] = id
            self.ids_persons[id] = person

        self.professions_ids = {}
        self.ids_professions = {}
        for line in FileUtils.read_file_as_list(PROFESSIONS_IDS_F):
            prof, id = line.split("\t", maxsplit=1)
            self.professions_ids[prof] = id
            self.ids_professions[id] = prof

        self.nationalities_ids = {}
        self.ids_nationalities = {}
        for line in FileUtils.read_file_as_list(NATIONALITIES_IDS_F):
            nation, id = line.split("\t", maxsplit=1)
            self.nationalities_ids[nation] = id
            self.ids_nationalities[id] = nation

        self.nationalities_countries = {}
        self.countries_nationalities = {}
        for line in FileUtils.read_file_as_list(COUNTRIES_NATIONALITIES_F):
            country, nation = line.split("\t", maxsplit=1)
            self.nationalities_countries[nation] = country
            self.countries_nationalities[country] = nation

    # -----------------
    # Methods

    # Persons - Person IDs
    def get_person_from_id(self, person_id):
        """Gets a person from a person_id.

        :param person_id: person ID.
        :return:
        """
        assert person_id in self.ids_persons, "Unknown person id: {}".format(person_id)
        return self.ids_persons[person_id]

    def get_id_from_person(self, person):
        """Gets a person ID from a person.

        :param person:
        :return:
        """
        if person == "Radu Goldiş":
            person = person.replace(S_CEDILLA, S_COMMA).replace(S_CEDILLA.upper(), S_COMMA.upper())  # hardcoded fixing
        assert person in self.persons_ids, "Unknown person: {}".format(person)
        # NO need to save and restore original value of person: it's immutable once exiting method
        return self.persons_ids[person]

    # Professions = Profession IDs
    def get_prof_from_id(self, prof_id):
        """Gets a profession from a profession ID.

        :param prof_id: profession ID.
        :return:
        """
        assert prof_id in self.ids_professions, "Unknown profession id: {}".format(prof_id)
        return self.ids_professions[prof_id]

    def get_id_from_prof(self, prof):
        """Gets a profession ID from a profession.

        :param prof: profession.
        :return:
        """
        assert prof in self.professions_ids, "Unknown profession: {}".format(prof)
        return self.professions_ids[prof]

    # Nationalities - Nationality IDs
    def get_nation_from_id(self, nation_id):
        """Gets a nationality from a nationality ID.

        :param nation_id: nationality ID.
        :return:
        """
        assert nation_id in self.ids_nationalities, "Unknown nationality id: {}".format(nation_id)
        return self.ids_nationalities[nation_id]

    def get_id_from_nation(self, nation):
        """Gets a nationality ID from a nationality.

        :param nation: nationality.
        :return:
        """
        assert nation in self.nationalities_ids, "Unknown nationality: {}".format(nation)
        return self.nationalities_ids[nation]

    # Countries - Nationalities
    def get_nation_from_country(self, country):
        """Gets a nationality from a country.

        :param country:
        :return:
        """
        assert country in self.countries_nationalities, "Unknown country: {}".format(country)
        return self.countries_nationalities[country]

    def get_country_from_nation(self, nation):
        """Gets a country from a nationality .

        :param nationality:
        :return:
        """
        assert nation in self.nationalities_countries, "Unknown nationality: {}".format(nation)
        return self.nationalities_countries[nation]
