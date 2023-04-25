import os
import json
import pymongo
from bson.objectid import ObjectId


#Get Amazon DocumentDB ceredentials from environment variables
username = os.environ.get("db_user")
password = os.environ.get("db_pass")
endpoint = os.environ.get("db_endpoint")


#Connect to Amazon DocumentDB
client = pymongo.MongoClient(endpoint, username=username, password=password,
        tls='true', tlsCAFile='rds-combined-ca-bundle.pem', retryWrites='false')
db = client.taxidb
taxi_col = db['taxi']

#Define error reporting function
def report_error(message):
    return {
        "statusCode": 400,
        "body": json.dumps({
            "message": message
        })  
    }

def lambda_handler(event, context):   

    print("Received data: ")
    print(event)
    taxi_data = {}

    taxi_data['email'] = event.get("email")
    if not taxi_data['email']:
        return report_error("Email is required")

    taxi_data['taxi_class'] = event.get("taxi_class", "Deluxe")

    taxi_data['first_name'] = event.get("first_name")
    taxi_data['last_name'] = event.get("last_name")


    # Check if email is already registered
    if taxi_col.find_one({"email": email}):
        return report_error("Email already registered")

    #Insert data
    result = taxi_col.insert_one(taxi_data)
    print(f"Inserted into taxi history: {result.inserted_id}")

    taxi_data['taxi_id'] = str(result.inserted_id)
    del taxi_data['_id']

    return {
        "statusCode": 200,
        "body": json.dumps(taxi_data)
    }



