import json
import os
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
taxi_collection = db['taxi']

def lambda_handler(event, context):
    print(event)

    if event.get('resource') == '/taxi/{id}':
        # Get single record by _id
        id = event['pathParameters']['id']
        print(id)
        result = taxi_collection.find_one({'_id': ObjectId(id)})
        print(result)
        result['_id'] = str(result['_id'])
        print(result)
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }

    # Get all all records
    cursor = taxi_collection.find()
    rows = []
    for row in cursor:
        row['_id'] = str(row['_id'])
        rows.append(row)
    print(rows)


    return {
        "statusCode": 200,
        "body": json.dumps(rows)
    }

