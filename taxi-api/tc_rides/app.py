import json
import os
import pymongo
from bson.objectid import ObjectId
from bson import json_util

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

def handle_get(event):
    print(event)
    query = event.get("queryStringParameters")
    if not query:
        query = {}

    if event.get('resource') == '/rides/{id}':
        # Get single record by _id
        id = event['pathParameters']['id']
        print(id)
        result = ride_collection.find_one({'_id': ObjectId(id)})
        print(result)
        result['_id'] = str(result['_id'])
        print(result)
        return {
            "statusCode": 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            "body": json_util.dumps(result)
        }

    # Get all records
    cursor = ride_collection.find(query)
    rows = []
    for row in cursor:
        row['_id'] = str(row['_id'])
        rows.append(row)
    print(rows)

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,OPTIONS"
        },
        "body": json_util.dumps(rows)
    }

def handle_post(event):
    print(event)
    print('ride lambda handler is called.')
    body = json.loads(event["body"])

    # Insert data
    result = ride_collection.insert_one(body)

    return {
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST'
        },
        "body": json.dumps({
            "ride_id": str(result.inserted_id),
            "message": "Ride created.",
        }),
    }


def handle_patch(event):
    print(event)
    id = event['pathParameters']['id']
    print(id)
    patch = {}
    for param in event["body"].split('&'):
        k, v = param.split('=')
        patch[k] = v
    result = ride_collection.update_one({'_id': ObjectId(id)}, {"$set": patch})

    return {
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST'
        },
        "body": json.dumps({
            "ride_id": str(result.upserted_id),
            "message": "Ride updated with taxi.",
        }),
    }


def handle_delete(event):
    print(event)
    if event.get('resource') == '/ride/{id}':
        # Get single record by _id
        id = event['pathParameters']['id']
        print(id)
        result = ride_collection.delete_one({'_id': ObjectId(id)})
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Ride id {id} deleted.",
            }),
        }


def handle_default(event):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Method not implemented",
        }),
    }

def lambda_handler(event, context):
    method = event["httpMethod"]
    if method == 'GET':
        return handle_get(event)
    elif method == 'POST':
        return handle_post(event)
    elif method == 'DELETE':
        return handle_delete(event)
    elif method == 'PATCH':
        return handle_patch(event)
    else:
        return handle_default(event)

