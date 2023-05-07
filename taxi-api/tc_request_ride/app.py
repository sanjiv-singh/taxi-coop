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
    origin = body["origin"] 
    destination = body["destination"]
    # UserID  - Input --> Check the User is present or not? - 400 series error

    # Contruct a mongodb location query and get the nearest taxi
    print('######################## CUSTOMER LOCATION ########################')
    start_location =  { '$geometry': { 
                type: "Point", 'coordinates': [origin] 
            }}
    pprint.pprint(start_location)   

    # Getting the nearest taxis to a customer
    print('######################## THE 2 NEAREST TAXIS ########################')
    nearest_query = {'location': {"$near":  start_location}}


    for doc in taxi_collection.find(nearest_query).limit(2):
        pprint.pprint(doc)
        near_taxi_collection.__add__(doc)


    return {
        "statusCode": 200,
        "body": json.dumps({
            "nearest_taxis": near_taxi_collection,
        }),
    }
