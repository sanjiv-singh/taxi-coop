import json
import os
import boto3

SOUTHWEST = os.environ['SOUTHWEST']
NORTHEAST = os.environ['NORTHEAST']

lambda_client = boto3.client('lambda')
iot_client = boto3.client('iot-data')


def lambda_handler(event, context):   
    taxi_list = json.loads(event["body"])
    result = publish_request(taxi_list)
    print(result)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Placed request for taxis {', '.join([taxi['taxi_id'] for taxi in taxi_list])}."
        })
    }

def publish_request(taxi_list):
    print(taxi_list)
    for taxi in taxi_list:
        taxi_id = taxi["taxi_id"]
        payload = json.dumps(taxi).encode('utf8')
        iot_client.publish(
            topic=f'iot/TAXI/{taxi_id}/request',
            qos=1,
            payload=payload 
        )

