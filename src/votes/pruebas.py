import time

from pymongo import MongoClient
from padron_web.settings import CONNECTION_STRING

client = MongoClient(CONNECTION_STRING)
db = client.padron_electoral
person_collection = db.votes_person
location_collection = db.votes_location

"""
person_collection.delete_many({"voting_board": "00000"})
location_collection.delete_many({"province": "ALAJUELA"})
location_collection.delete_many({"province": "SAN JOSE"})
location_collection.delete_many({"province": "LIMON"})
location_collection.delete_many({"province": "HEREDIA"})
location_collection.delete_many({"province": "CARTAGO"})
location_collection.delete_many({"province": "PUNTARENAS"})
location_collection.delete_many({"province": "GUANACASTE"})
location_collection.delete_many({"province": "CONSULADO"})"""

"""locations_to_find = {"province": "ALAJUELA"}

criteria = [{"$match": {"full_name": {"$regex": "GREGORY"}, "gender": "Mujer"}}, {"$count": "mujeres"}]

temp_locations_list = location_collection.find(locations_to_find)

criterio = [{"$match": {"full_name": {"$regex": "GREGORY"}, "gender": "Hombre"}}, {"$count": "hombres"}]
results = {}
results.update(person_collection.aggregate(criteria).next())
results.update(person_collection.aggregate(criterio).next())


print(results)
print(f"The type of results is: {type(results)}")
for result in results:
    print(result)
    print(type(result))"""

document_to_find = [{"$match": {"gender": "Mujer", "elec_code_id.province": "ALAJUELA",
                                            "elec_code_id.canton": "NARANJO"}},
                                {"$group": {"_id": "$elec_code_id.district", "count": {"$sum": 1}}}]

document_to_fi = [{"$match": {"gender": "Mujer", "elec_code_id.province": "ALAJUELA"}},
                    {"$group": {"_id": "$elec_code_id.district", "count": {"$sum": 1}}}]
document = [{"$match": {"elec_code_id.canton": "NARANJO"}}, {"$group": {"_id": "$gender", "count": {"$sum": 1}}}]
doc = [{"$match": {"elec_code_id.district": "SAN ANTONIO DE BARRANCA"}}, {"$group": {"_id": "$gender", "count": {"$sum": 1}}}]

pipeline = [document_to_find, document, doc]

values = [[{"$match": {"gender": "Mujer", "elec_code_id.province": "ALAJUELA"}},
                    {"$group": {"_id": "$elec_code_id.canton", "count": {"$sum": 1}}}]]

result = person_collection.aggregate(document_to_find)

for x in result:
    print(x)


