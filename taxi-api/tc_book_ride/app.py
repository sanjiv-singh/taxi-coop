import json
import os
import pymongo
import pprint
from bson.objectid import ObjectId
import boto3

#Get Amazon DocumentDB ceredentials from environment variables
username = os.environ.get("db_user")
password = os.environ.get("db_pass")
endpoint = os.environ.get("db_endpoint")

SOUTHWEST = os.environ['SOUTHWEST']
NORTHEAST = os.environ['NORTHEAST']
REGISTER_LAMBDA_ARN = os.environ['register_lambda_arn']
IOT_POLICY = os.environ['iot_policy']
IOT_THING_TYPE = os.environ['iot_thing_type']
IOT_THING_GROUP = os.environ['iot_thing_group']

lambda_client = boto3.client('lambda')
iot_client = boto3.client('iot-data')
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iot-data.html

#Connect to Amazon DocumentDB
client = pymongo.MongoClient(endpoint, username=username, password=password,
    tls='true', tlsCAFile='rds-combined-ca-bundle.pem', retryWrites='false')
db = client.taxidb
print("Connected to Amazon DocumentDB")
taxi_collection = db['taxi']

def lambda_handler(event, context):   
    body = json.loads(event["body"])   
    publish_booked_taxi(body)

    return {
        "statusCode": 200,
        "body":"updated succesfully",
    }

def publish_booked_taxi(taxi_data):
    taxi_id =taxi_data["taxi_id"]
    print('publish booked taxi')
    return iot_client.publish(
    topic=f'iot/TAXI/{taxi_id}/book',
    qos=1,
    payload=taxi_data 
    )

     