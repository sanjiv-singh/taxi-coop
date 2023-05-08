import json
import os
import pymongo
import pprint
from bson.objectid import ObjectId

#Get Amazon DocumentDB ceredentials from environment variables
username = os.environ.get("db_user")
password = os.environ.get("db_pass")
endpoint = os.environ.get("db_endpoint")

SOUTHWEST = os.environ['SOUTHWEST']
NORTHEAST = os.environ['NORTHEAST']

#Connect to Amazon DocumentDB
client = pymongo.MongoClient(endpoint, username=username, password=password,
    tls='true', tlsCAFile='rds-combined-ca-bundle.pem', retryWrites='false')
db = client.taxidb
print("Connected to Amazon DocumentDB")
taxi_collection = db['taxi']

def lambda_handler(event, context):

    near_taxi_collection = []
    body = json.loads(event["body"])
    taxi_class = body["taxi_class"]
    origin = [float(coord) for coord in body["origin"].split(',')]
    origin.reverse()
    destination = [float(coord) for coord in body["destination"].split(',')]
    destination.reverse()
    # UserID  - Input --> Check the User is present or not? - 400 series error

    # Contruct a mongodb location query and get the nearest taxi
    print('######################## CUSTOMER LOCATION ########################')
    start_location =  { '$geometry': { 
                "type": "Point", 'coordinates': origin 
            }}
    pprint.pprint(start_location)   

    # Getting the nearest taxis to a customer
    # Find the nearest taxis that are available and are of requested class
    print('######################## THE 2 NEAREST TAXIS ########################')
    nearest_query = {'location': {"$near":  start_location}, 'taxi_class': taxi_class, 'status': 1}


    for doc in taxi_collection.find(nearest_query).limit(2):
        doc['taxi_id'] = str(doc['_id'])
        del doc["_id"]
        pprint.pprint(doc)
        near_taxi_collection.append(doc)


    return {
        "statusCode": 200,
        "body": json.dumps({
            "nearest_taxis": near_taxi_collection,
        }),
    }
