import os
import json
import pymongo
from bson.objectid import ObjectId
import asyncio


#Get Amazon DocumentDB ceredentials from environment variables
username = os.environ.get("db_user")
password = os.environ.get("db_pass")
endpoint = os.environ.get("db_endpoint")

# Get the Bounding Box northing and easting values from environment variables
north = float(os.environ.get("north"))
west = float(os.environ.get("west"))
south = float(os.environ.get("south"))
east = float(os.environ.get("east"))

#Connect to Amazon DocumentDB
client = pymongo.MongoClient(endpoint, username=username, password=password,
        tls='true', tlsCAFile='rds-combined-ca-bundle.pem', retryWrites='false')
db = client.taxidb
taxi_collection = db['taxi']
taxi_history = db['taxi_history']

def report_error(error_message):
    return {
        'statusCode': 400,
        'body': json.dumps(error_message)
    }

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

    # Extract the latitude and longitude from the event
    lat = taxi_data.get("location")["coordinates"][1]
    lng = taxi_data.get("location")["coordinates"][0]

    # Check if the requested location is in the bounding box
    if south <= float(lat) <= north and west <= float(lng) <= east:
        asyncio.get_event_loop().run_until_complete(insert_taxi_history(taxi_data))
        asyncio.get_event_loop().run_until_complete(update_taxi_collection(taxi_data))
    else:
        return report_error("Taxi is not in the bounding box")



