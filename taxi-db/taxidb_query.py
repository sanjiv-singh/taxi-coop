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

def report_error(error_message):
    return {
        'statusCode': 400,
        'body': json.dumps(error_message)
    }

def lambda_handler(event, context):   

    print("Received data: ")
    print(event)
    collection_text = event.get("collection")
    if collection_text is None:
        print("No collection provided, using taxi collection as default")
        collection_text = "taxi"
    collection = db[collection_text]

    query = event.get("query")
    print(f"Query: {query}")
    limit = event.get("limit")

    if query is None:
        cursor = collection.find()
    else:
        cursor = collection.find(query)
    
    if limit:
        cursor = cursor.limit(limit)

    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    print(f"Found {len(results)} results")
    if len(results) == 0:
        return report_error("No results found")
    if len(results) == 1:
        return {
            'statusCode': 200,
            'body': json.dumps(results[0])
        }
    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }



