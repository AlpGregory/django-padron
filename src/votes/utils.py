import datetime

from django.http import HttpResponseRedirect

from padron_web.settings import ACTUAL_DATABASE
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger
from django.db.models.signals import pre_save
from django.dispatch import receiver
from votes.models import Person, Location
from pymongo import MongoClient
from padron_web.settings import CONNECTION_STRING
from django.db import connection
from django.db import IntegrityError, ProgrammingError, DatabaseError, InterfaceError, DataError, OperationalError, \
    NotSupportedError
from django.db.models import Count, Q

logger = getLogger(__name__)


@receiver(pre_save, sender=Person)
def add_voter(sender, instance, **kwargs):
    """
    This method checkout for all attributes to be in the right format

    :param sender: Person Model
    :param instance: the person to be saved
    :param kwargs: other params
    """
    instance.voting_board = '00000'
    instance.full_name = instance.full_name.upper()
    if len(instance.identification) > 3:
        instance.gender = "Hombre" if int(instance.identification[3]) % 2 == 0 else "Mujer"


def set_expiration_date(string_date):
    """
    Expiration is taken as a string a given as a date

    :param string_date: a string with the id's expiration date.
    :return: The expiration date as a Date type
    """
    # Format: year, month, day
    date = datetime.date(int(string_date[:4]), int(string_date[4:6]), int(string_date[6:]))

    return date


def set_database():
    if ACTUAL_DATABASE == "Mongodb":
        return MongoDB()
    elif ACTUAL_DATABASE == "Postgresql":
        return PostgresqlDB()


class FileDecoder:
    """
    A class to decode two given txt files and upload the data to a database.

    ...

    Attributes
    ----------
    __distelec_file_sections : list
        Stores the data of Distelec.txt by sections
    __padron_file_sections : list
        Stores the data of PADRON_COMPLETO.txt by sections
    __SPLIT_LOCATIONS : int
        The amount of lines stored in a single section of _distelec_file_sections
    __SPLIT_PEOPLE : int
        The amount of lines stored in a single section of _padron_file_sections
    """

    def __init__(self):
        self.__distelec_file_sections = []
        self.__padron_file_sections = []
        self.__SPLIT_LOCATIONS = 1072
        self.__SPLIT_PEOPLE = 8324
        self.__DATABASE = set_database()

    def process_files(self, locations_path, people_path):
        """
        A files processor manager. Creates the Thread Pools to accelerate the upload process.

        :param locations_path: A string with the Distelec.txt directory
        :param people_path: A string with the PADRON_COMPLETO.txt directory
        """
        self.__split_locations_file(locations_path)
        self.__split_people_file(people_path)

        with ThreadPoolExecutor(max_workers=2) as executor:
            for section in self.__distelec_file_sections:
                executor.submit(self.__set_location_tuples, section)

        with ThreadPoolExecutor(max_workers=8) as executor:
            for section in self.__padron_file_sections:
                executor.submit(self.__set_person_tuples, section)

    def __split_locations_file(self, file_path):
        """
        Reads an entire txt file and split it in sections with certain amount of lines.

        :param file_path: A string with the .txt file directory
        """
        with open(file_path, 'r', encoding='iso-8859-1') as file:
            string_file = file.read().splitlines()
            splits = len(string_file) // self.__SPLIT_LOCATIONS

            counter = 0

            for i in range(0, splits):
                self.__distelec_file_sections.append(string_file[counter:counter + self.__SPLIT_LOCATIONS])
                counter += self.__SPLIT_LOCATIONS

            self.__distelec_file_sections.append(string_file[counter:])

    def __split_people_file(self, file_path):
        """
        Reads an entire txt file and split it in sections with certain amount of lines.

        :param file_path: A string with the .txt file directory
        """
        with open(file_path, 'r', encoding='iso-8859-1') as file:
            string_file = file.read().splitlines()
            splits = len(string_file) // self.__SPLIT_PEOPLE

            counter = 0

            for i in range(0, splits):
                self.__padron_file_sections.append(string_file[counter:counter + self.__SPLIT_PEOPLE])
                counter += self.__SPLIT_PEOPLE

            self.__padron_file_sections.append(string_file[counter:])

    def __set_person_tuples(self, people_list):
        """
        Set some PADRON_COMPLETO.txt section into useful data and adds it as a tuple to a list.

        :param people_list: The section of the file.
        """
        count = 0
        person_tuples = []
        for line in people_list:
            person_values = line.split(',')
            identification = person_values[0]
            elec_code = person_values[1]
            voting_board = person_values[4]
            full_name = f"{person_values[5].strip()} {person_values[6].strip()} {person_values[7].strip()}"
            gender = "Hombre" if int(person_values[0][3]) % 2 == 0 else "Mujer"
            id_expiration_date = set_expiration_date(person_values[3])

            person_tuples.append((identification, voting_board, full_name, gender, id_expiration_date, elec_code))

            count += 1

        self.__DATABASE.load_people_data(tuples=person_tuples)

    def __set_location_tuples(self, location_list):
        """
        Set some Distelec.txt section into useful data and adds it as a tuple to a list.

        :param location_list: The section of the file.
        :return:
        """
        count = 0
        location_tuples = []
        for line in location_list:
            location_values = line.split(',')
            elec_code = location_values[0]
            province = location_values[1]
            canton = location_values[2]
            district = location_values[3].strip()

            location_tuples.append((elec_code, province, canton, district))

            count += 1

        self.__DATABASE.load_location_data(tuples=location_tuples)


class DBFactory(ABC):
    """
    Abstract factory class for database processes
    """

    @abstractmethod
    def load_people_data(self, tuples):
        """
        Loads some person tuples/documents to the database
        :param tuples: a list of voters tuples
        """
        pass

    @abstractmethod
    def load_location_data(self, tuples):
        """
        Loads some location tuples/documents to the database
        :param tuples: a list of vote locations
        """
        pass

    @abstractmethod
    def search_voters(self, identification, name):
        """
        Search in database for voters who match with the specified identification or name
        :param identification: a string with an alike voter id
        :param name: a string with an alike voter name
        :return: a list of voters who match the specifications
        """
        pass

    @abstractmethod
    def get_voter_statistics(self, id_expiration_date, elec_code):
        """
        Shows the amount of voters by gender in its district, canton and province, also shows the amount of voters with
        the same identification expiration date
        :param id_expiration_date: a datefield
        :param elec_code: the voter's electoral code
        :return: a list with all the statistics
        """
        pass

    @abstractmethod
    def get_voter(self, identification):
        """
        Search for all the voter's info
        :param identification: a string
        :return: a person object
        """
        pass

    @abstractmethod
    def add_voter(self, person):
        """
        Inserts a row/document on the database with a new person's info
        :param person: a dictionary with the fields of the form
        :return: the person identification
        """
        pass

    @abstractmethod
    def delete_voter(self, identification):
        """
        Deletes a voter from the database.
        :param identification: the voter's identification
        """
        pass


class MongoDB(DBFactory, ABC):
    def __init__(self):
        self.client = MongoClient(CONNECTION_STRING)
        self.db = self.client.padron_electoral
        self.person_collection = self.db.votes_person
        self.location_collection = self.db.votes_location
        self.locations_list = []

    def get_location_info(self, elec_code_id):

        for location in self.locations_list:
            if elec_code_id == location.elec_code:

                return location

        return None

    def load_people_data(self, tuples):

        list_of_documents = []

        for tuple in tuples:
            elec_code = self.get_location_info(tuple[5])
            if elec_code is not None:
                date = f'{tuple[4].strftime("%Y")}-{tuple[4].strftime("%m")}-{tuple[4].strftime("%d")}'
                person_document = {
                    "_id": tuple[0],
                    "voting_board": tuple[1],
                    "full_name": tuple[2],
                    "gender": tuple[3],
                    "id_expiration_date": date,
                    "elec_code_id": {
                        "elec_code": elec_code.elec_code,
                        "province": elec_code.province,
                        "canton": elec_code.canton,
                        "district": elec_code.district
                    }
                }
                list_of_documents.append(person_document)

        try:
            self.person_collection.insert_many(list_of_documents)
        except Exception as error:  # Cambiar exception
            print(error)
            logger.error("Error importing voters data", exc_info=error)

    def load_location_data(self, tuples):

        list_of_documents = []

        for tuple in tuples:
            location_document = {
                "_id": tuple[0],
                "province": tuple[1],
                "canton": tuple[2],
                "district": tuple[3]
            }
            location = Location(elec_code=tuple[0], province=tuple[1], canton=tuple[2], district=tuple[3])
            self.locations_list.append(location)
            list_of_documents.append(location_document)

        try:
            self.location_collection.insert_many(list_of_documents)
        except Exception as error:
            print(error)
            logger.error("Error importing locations data", exc_info=error)

    def search_voters(self, identification, name):
        cursor = []
        voters_info_list = []

        if identification != '':
            documents_to_find = {"_id": {"$regex": identification}}
            cursor = self.person_collection.find(documents_to_find)
        elif name != '':
            documents_to_find = {"full_name": {"$regex": name}}
            cursor = self.person_collection.find(documents_to_find)

        for doc in cursor:
            person = Person(identification=doc["_id"], full_name=doc["full_name"])

            voters_info_list.append(person)

        return voters_info_list

    def get_voter_statistics(self, id_expiration_date, elec_code):
        counts_list = []
        province = elec_code.province
        canton = elec_code.canton
        district = elec_code.district
        women_by_province = 0
        women_by_canton = 0
        women_by_district = 0
        men_by_province = 0
        men_by_canton = 0
        men_by_district = 0

        pipeline = [{"$match": {"elec_code_id.province": province}},
                    {"$group": {"_id": "$gender", "count": {"$sum": 1}}}]

        province_stats = self.person_collection.aggregate(pipeline)

        for group in province_stats:
            if group["_id"] == "Mujer":
                women_by_province = group["count"]

            if group["_id"] == "Hombre":
                men_by_province = group["count"]

        pipeline = [{"$match": {"gender": "Mujer", "elec_code_id.province": province, "elec_code_id.canton": canton}},
                    {"$group": {"_id": "$elec_code_id.district", "count": {"$sum": 1}}}]

        women_district_stats = self.person_collection.aggregate(pipeline)

        for group in women_district_stats:
            women_by_canton += group['count']
            if group['_id'] == district:
                women_by_district = group['count']

        pipeline = [{"$match": {"gender": "Hombre", "elec_code_id.province": province, "elec_code_id.canton": canton}},
                    {"$group": {"_id": "$elec_code_id.district", "count": {"$sum": 1}}}]

        men_district_stats = self.person_collection.aggregate(pipeline)

        for group in men_district_stats:
            men_by_canton += group['count']
            if group['_id'] == district:
                men_by_district = group['count']

        same_exp_date = self.person_collection.count_documents({
            "id_expiration_date": f'{id_expiration_date.strftime("%Y")}-{id_expiration_date.strftime("%m")}'
                                  f'-{id_expiration_date.strftime("%d")}'
        })

        counts_list.extend([men_by_district + women_by_district,
                            men_by_canton + women_by_canton,
                            men_by_province + women_by_province,
                            men_by_district, men_by_canton,
                            men_by_province, women_by_district,
                            women_by_canton, women_by_province,
                            same_exp_date])

        return counts_list

    def get_voter(self, identification):
        person_to_find = {"_id": identification}
        person = self.person_collection.find_one(person_to_find)
        person_found = None

        if person:
            elec_code_id = person["elec_code_id"]

            date = datetime.date(int(person["id_expiration_date"][:4]), int(person["id_expiration_date"][5:7]),
                                 int(person["id_expiration_date"][8:]))
            elec_code = Location(elec_code=elec_code_id["elec_code"], province=elec_code_id["province"],
                                 canton=elec_code_id["canton"], district=elec_code_id["district"])

            person_found = Person(identification=person["_id"], elec_code=elec_code,
                                  voting_board=person["voting_board"], full_name=person["full_name"],
                                  gender=person["gender"], id_expiration_date=date)

        return person_found

    def add_voter(self, person):
        location = person["elec_code"]
        elec_code_id = self.location_collection.find_one({"province": location.province, "canton": location.canton,
                                                          "district": location.district})["_id"]
        person["full_name"] = person["full_name"].upper()
        if len(str(person["identification"])) > 3:
            person["gender"] = "Hombre" if int(str(person["identification"])[3]) % 2 == 0 else "Mujer"

        new_person = {
            "_id": str(person["identification"]),
            "elec_code_id": elec_code_id,
            "voting_board": "00000",
            "full_name": person["full_name"],
            "gender": person["gender"],
            "id_expiration_date": f'{person["id_expiration_date"].strftime("%Y")}-{person["id_expiration_date"].strftime("%m")}'
                                  f'-{person["id_expiration_date"].strftime("%d")}'
        }

        try:
            result = self.person_collection.insert_one(new_person)
        except Exception as error:
            print(error)

        return str(person["identification"])

    def delete_voter(self, identification):
        person_to_delete = {"_id": identification}
        self.person_collection.delete_one(person_to_delete)


class PostgresqlDB(DBFactory, ABC):

    def load_people_data(self, tuples):
        cursor = None

        try:
            cursor = connection.cursor()

            data_text = ','.join(cursor.mogrify('(%s, %s, %s, %s, %s, %s)', row).decode(
                'utf-8') for row in tuples)

            insert_script = """INSERT INTO public.votes_person (identification, voting_board, full_name, gender,  
                            id_expiration_date, elec_code_id) VALUES {0} \nON CONFLICT (
                            identification)\nDO NOTHING;""".format(data_text)

            cursor.execute(insert_script)
            connection.commit()

        except (IntegrityError, ProgrammingError, DatabaseError, InterfaceError, DataError, OperationalError,
                NotSupportedError) as error:
            print(error)
            logger.error("Error importing voters data", exc_info=error)

        finally:
            if cursor is not None:
                cursor.close()

    def load_location_data(self, tuples):
        cursor = None

        try:
            cursor = connection.cursor()

            data_text = ','.join(cursor.mogrify('(%s, %s, %s, %s)', row).decode(
                'utf-8') for row in tuples)

            insert_script = """INSERT INTO public.votes_location (elec_code, province, canton, district) 
                            VALUES {0} \nON CONFLICT (elec_code)\nDO NOTHING;""".format(data_text)

            cursor.execute(insert_script)
            connection.commit()

        except (IntegrityError, ProgrammingError, DatabaseError, InterfaceError, DataError, OperationalError,
                NotSupportedError) as error:
            print(error)
            logger.error("Error importing locations data", exc_info=error)

        finally:
            if cursor is not None:
                cursor.close()

    def search_voters(self, identification, name):
        """
            Looks for voters in the DB who match the searching specifications.

            :param identification: the value of 'identification' input
            :param name: the value of 'name' input
            :return: a list with all the found objects
            """
        voters_info_list = []

        if identification != '':
            voters_info_list = Person.objects.filter(identification__contains=identification)
        elif name != '':
            voters_info_list = Person.objects.filter(full_name__contains=name)

        return voters_info_list

    def get_voter_statistics(self, id_expiration_date, elec_code):
        """
                Retrieves some statistics associated to the voter. Like voters in their region and so.

                :param id_expiration_date: the voters id's expiration date
                :param elec_code: the chose voter's electoral code in a Location object
                :return:a list with the obtained statistics
                """
        counts_list = []
        province = elec_code.province
        canton = elec_code.canton
        district = elec_code.district
        counts = Person.objects.aggregate(women_by_province=Count('identification',
                                                                  filter=Q(elec_code__province=province,
                                                                           gender='Mujer')),
                                          women_by_canton=Count('identification',
                                                                filter=Q(elec_code__canton=canton, gender='Mujer')),
                                          women_by_district=Count('identification',
                                                                  filter=Q(elec_code__district=district,
                                                                           gender='Mujer')),
                                          men_by_province=Count('identification',
                                                                filter=Q(elec_code__province=province,
                                                                         gender='Hombre')),
                                          men_by_canton=Count('identification',
                                                              filter=Q(elec_code__canton=canton, gender='Hombre')),
                                          men_by_district=Count('identification',
                                                                filter=Q(elec_code__district=district,
                                                                         gender='Hombre')),
                                          same_exp_date=Count('identification',
                                                              filter=Q(id_expiration_date=id_expiration_date))
                                          )

        counts_list.extend([counts['men_by_district'] + counts['women_by_district'],
                            counts['men_by_canton'] + counts['women_by_canton'],
                            counts['men_by_province'] + counts['women_by_province'],
                            counts['men_by_district'], counts['men_by_canton'],
                            counts['men_by_province'], counts['women_by_district'],
                            counts['women_by_canton'], counts['women_by_province'],
                            counts['same_exp_date']])

        return counts_list

    def get_voter(self, identification):
        result = Person.objects.filter(pk=identification)
        person = None

        if result.exists():
            person = result[0]
            return person

        return person

    def add_voter(self, person):
        elec_code = Location.objects.filter(province=person["elec_code"].province, canton=person["elec_code"].canton,
                                            district=person["elec_code"].district)

        if elec_code.exists():
            new_person = Person(identification=str(person["identification"]), elec_code=elec_code[0],
                                full_name=person["full_name"], id_expiration_date=person["id_expiration_date"])
            new_person.save()

        return str(person["identification"])

    def delete_voter(self, identification):
        person = Person.objects.filter(pk=identification)

        if person.exists():
            person[0].delete()
