import os
import json
import pymongo
from bson.objectid import ObjectId


#Get Amazon DocumentDB ceredentials from environment variables
username = os.environ.get("db_user")
password = os.environ.get("db_pass")
endpoint = os.environ.get("db_endpoint")

def lambda_handler(event, context):   

    print("Received data: ")
    print(event)
    taxi_data = event

    #Connect to Amazon DocumentDB
    client = pymongo.MongoClient(endpoint, username=username, password=password,
            tls='true', tlsCAFile='rds-combined-ca-bundle.pem', retryWrites='false')
    db = client.taxidb
    taxi_collection = db['taxi']
    taxi_history = db['taxi_history']

    #Insert data
    result = taxi_history.insert_one(taxi_data)
    print(f"Inserted into taxi history: {result.inserted_id}")

    #Update data
    taxi_data['_id'] = ObjectId(taxi_data['taxi_id'])
    del taxi_data['taxi_id']
    result = taxi_collection.replace_one({"_id": taxi_data["_id"]}, taxi_data, upsert=True)
    print(f"Updated {result.matched_count} item in taxi collection: {result.upserted_id}")

    #Close connection
    client.close()

