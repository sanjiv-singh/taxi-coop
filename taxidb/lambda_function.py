import os
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
    print("connecting to taxidb")
    client = pymongo.MongoClient(clusterendpoint, username=username, password=password, tls='true', tlsCAFile='rds-combined-ca-bundle.pem',retryWrites='false')
    print("connected")
    db = client.taxidb
    print(db)
    profiles = db['profiles']
    print(profiles)

    #Insert data
    print("inserting data to profiles collection")
    profiles.insert_many(SEED_DATA)
    print("Successfully inserted data")

    #Find a document
    query = {'name': 'Jane'}
    print("Printing query results")
    print(profiles.find_one(query))

    #Update a document
    print("Updating document")
    profiles.update_one(query, {'$set': {'level': 4}})
    print(profiles.find_one(query))

    #Clean up
    db.drop_collection('profiles')
    client.close()

