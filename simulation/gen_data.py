import json
import os
import pymongo
import time
import random

username = os.environ.get("DB_USER")
password = os.environ.get("DB_PASSWORD")
endpoint = os.environ.get("DB_ENDPOINT")

SOUTHWEST = 12.8, 77.5 
NORTHEAST = 13.5, 78.2

AIRPORT = 13.1989, 77.7068
KASTURI_NAGAR = 13.0061, 77.6594

#Connect to Amazon DocumentDB
client = pymongo.MongoClient(endpoint, username=username, password=password,
    tls='true', tlsCAFile='rds-combined-ca-bundle.pem', retryWrites='false')
db = client.taxidb
print("Connected to Amazon DocumentDB")
ride_collection = db['ride']


# Function to create a random location
def create_random_location():
    lat = random.uniform(SOUTHWEST[0], NORTHEAST[0])
    lng = random.uniform(SOUTHWEST[1], NORTHEAST[1])
    return [lng, lat]

# Function to create a random location based
# on normal distribution around a given location
def create_random_location_around(location):
    while True:
        lat = random.normalvariate(location[0], 0.01)
        lng = random.normalvariate(location[1], 0.01)
        if lat < SOUTHWEST[0] or lat > NORTHEAST[0]:
            continue
        if lng < SOUTHWEST[1] or lng > NORTHEAST[1]:
            continue
        break
    return [lng, lat]

# Generate data for the ride collection
# Use normal distribution to generate random lat/long
# around a few randomly selected points in Bengaluru

for _ in range(1000):
    origin = create_random_location_around(random.choice([AIRPORT, KASTURI_NAGAR]))
    destination = create_random_location()
    ride = {
        "origin": {
            "type": "Point",
            "coordinates": origin
        },
        "destination": {
            "type": "Point",
            "coordinates": destination
        },
        "status": random.choice(["COMPLETED", "CANCELLED"])
    }
    #ride_collection.insert_one(ride)
    print(f"Inserted ride: {ride}")
