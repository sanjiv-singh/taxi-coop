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
user_collection = db['user']

def report_error(message):
    return {
        "statusCode": 400,
        "body": json.dumps({
            "message": message,
        }),
    }

def handle_get(event):
    print(event)
    if event.get('resource') == '/user/{id}':
        # Get single record by _id
        id = event['pathParameters']['id']
        print(id)
        result = user_collection.find_one({'_id': ObjectId(id)})
        print(result)
        result['_id'] = str(result['_id'])
        print(result)
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }

    # Get all all records
    cursor = user_collection.find()
    rows = []
    for row in cursor:
        row['_id'] = str(row['_id'])
        rows.append(row)
    print(rows)


    return {
        "statusCode": 200,
        "body": json.dumps(rows)
    }

def handle_post(event):
    print(event)
    print('user lamda handler is called.')
    body = json.loads(event["body"])
    email = body.get('email')
    if not email:
        report_error("Email is required")
    pprint.pprint(body)

   #Insert data
    try:
        result = user_collection.insert_one(body)  
        user_id = str(result.inserted_id)
    except Exception as e:
        return report_error(str(e))

    return {
        "statusCode": 200,
        "body": json.dumps({"user_id": user_id})
    }
    
def handle_delete(event):
    id = event['pathParameters']['id']
    print(id)
    result = user_collection.delete_one({'_id': ObjectId(id)})
    print(result)
    result['_id'] = str(result['_id'])
    print(result)
        
    return {
            "statusCode": 200,
            "body": json.dumps(result)
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
    else:
        return handle_default(event)

