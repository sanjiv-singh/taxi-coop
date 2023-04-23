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
user_collection = db['users']

def lambda_handler(event, context):
    print(event)
    print('user lamda handler is called.')


    body = json.loads(event["body"])
    first_name = body["first_name"]
    last_name = body["last_name"]
    email = body["email"]
 
 
    pprint.pprint(first_name)
    pprint.pprint(last_name) 

   #Insert data
    result = user_collection.insert_one(body)
    print(f"Inserted into taxi history: {result.inserted_id}")
    

    return {
        "statusCode": 200,
        "body": "User registration is successful."        
    }
