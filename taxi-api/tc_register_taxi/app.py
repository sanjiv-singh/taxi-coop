import json
import os
import boto3

REGISTER_LAMBDA_ARN = os.environ['register_lambda_arn']

lambda_client = boto3.client('lambda')
iot_client = boto3.client('iot')

def register_taxi_in_db(taxi_data):
    response = lambda_client.invoke(
        FunctionName=REGISTER_LAMBDA_ARN,
        InvocationType='RequestResponse',
        Payload=json.dumps(taxi_data)
    )
    return response

def register_taxi_in_iot(taxi_data):
    print(taxi_data)
    #response = iot_client.create_thing(
    #    thingName=taxi_data['taxi_id']
    #)
    #print( response)
    response = iot_client.create_keys_and_certificate(
        setAsActive=True
    )
    return response

def lambda_handler(event, context):
    body = json.loads(event["body"])
    taxi_data = {
            "email": body.get("email"),
            "first_name": body.get("first_name"),
            "last_name": body.get("last_name"),
            "taxi_class": body.get("taxi_class", "Deluxe")
    }
    response = register_taxi_in_db(taxi_data)
    payload = response["Payload"].read()
    taxi_data = json.loads(payload.decode('utf-8')).get("body")
    print(taxi_data)
    response = register_taxi_in_iot(taxi_data)
    print(response)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Taxi registered successfully",
            "taxi_data": taxi_data
        }),
    }