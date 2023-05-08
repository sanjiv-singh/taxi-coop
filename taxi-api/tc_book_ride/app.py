import json
import os
import boto3

SOUTHWEST = os.environ['SOUTHWEST']
NORTHEAST = os.environ['NORTHEAST']

lambda_client = boto3.client('lambda')
iot_client = boto3.client('iot-data')
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iot-data.html


def lambda_handler(event, context):   
    body = json.loads(event["body"])
    result = publish_booked_taxi(body)
    print(result)

    return {
        "statusCode": 200,
        "body": {
            "message": "updated succesfully"
        }
    }

def publish_booked_taxi(taxi_data):
    taxi_id =taxi_data["taxi_id"]
    payload = json.dumps(taxi_data).encode('utf8')
    print('publish booked taxi')
    return iot_client.publish(
        topic=f'iot/TAXI/{taxi_id}/book',
        qos=1,
        payload=payload 
    )

