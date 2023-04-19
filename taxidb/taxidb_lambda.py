import os
import json
import pymongo


#Insert sample data
SEED_DATA = [
{ "_id" : 1, "name" : "Terry", "status": "active", "level": 12, "score":202},
{ "_id" : 2, "name" : "John", "status": "inactive", "level": 2, "score":9},
{ "_id" : 3, "name" : "Mary", "status": "active", "level": 7, "score":87},
{ "_id" : 4, "name" : "Jane", "status": "active", "level": 3, "score":27}
]

#Get Amazon DocumentDB ceredentials from environment variables
username = os.environ.get("db_user")
password = os.environ.get("db_pass")
clusterendpoint = os.environ.get("db_endpoint")

def lambda_handler(event, context):   

    taxi_data = event
    print(taxi_data)

    #Connect to Amazon DocumentDB
    client = pymongo.MongoClient(clusterendpoint, username=username, password=password, tls='true', tlsCAFile='rds-combined-ca-bundle.pem',retryWrites='false')
    db = client.taxidb
    taxi_collection = db['taxies']

    #Insert data
    taxi_collection.insert_one(event)
    print("Successfully inserted data")

    client.close()

