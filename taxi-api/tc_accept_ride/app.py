import json
import os
import datetime
import pymongo
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
ride_collection = db['ride']

def report_error(message):
    return {
        "statusCode": 400,
        "body": json.dumps({
            "message": message,
        }),
    }

def lambda_handler(event, context):
    print(event)
    body = json.loads(event["body"])
    taxi_id = body.get('taxi_id')
    ride_id = body.get('ride_id')
    accepted_taxi = {
        "taxi_id": taxi_id,
        "timestamp": datetime.datetime.now()
    }
    result = ride_collection.update_one({'_id': ObjectId(ride_id)}, {'$push': {'accepted_taxis': accepted_taxi}})
    print(f'Modified {result.modified_count} rides')

    return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Taxi {taxi_id} accepted ride {ride_id}",
            }),
    }
    
