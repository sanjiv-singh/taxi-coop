import os
import json
import pymongo
from bson.objectid import ObjectId
import asyncio


#Get Amazon DocumentDB ceredentials from environment variables
username = os.environ.get("db_user")
password = os.environ.get("db_pass")
endpoint = os.environ.get("db_endpoint")

#Connect to Amazon DocumentDB
client = pymongo.MongoClient(endpoint, username=username, password=password,
        tls='true', tlsCAFile='rds-combined-ca-bundle.pem', retryWrites='false')
db = client.taxidb
taxi_collection = db['taxi']
taxi_history = db['taxi_history']

async def update_taxi_collection(taxi_data):
    #Update data
    taxi_data['_id'] = ObjectId(taxi_data['taxi_id'])
    del taxi_data['taxi_id']
    result = taxi_collection.replace_one({"_id": taxi_data["_id"]}, taxi_data, upsert=True)
    print(f"Updated {result.matched_count} item in taxi collection: {result.upserted_id}")

async def insert_taxi_history(taxi_data):
    #Insert data
    result = taxi_history.insert_one(taxi_data)
    print(f"Inserted into taxi history: {result.inserted_id}")


def lambda_handler(event, context):   

    print("Received data: ")
    print(event)
    taxi_data = event

    asyncio.get_event_loop().run_until_complete(insert_taxi_history(taxi_data))
    asyncio.get_event_loop().run_until_complete(update_taxi_collection(taxi_data))

