import json
import os
import boto3

REGISTER_LAMBDA_ARN = os.environ['register_lambda_arn']
IOT_POLICY = os.environ['iot_policy']
IOT_THING_TYPE = os.environ['iot_thing_type']
IOT_THING_GROUP = os.environ['iot_thing_group']

lambda_client = boto3.client('lambda')
iot_client = boto3.client('iot')


def create_certificate():
    resp = iot_client.create_keys_and_certificate(setAsActive=True)
    data = json.loads(json.dumps(resp, sort_keys=False, indent=4))
    for element in data:
        if element == 'certificateArn':
            cert_arn = data['certificateArn']
        if element == 'certificatePem':
            cert_pem = data['certificatePem']
        if element == 'keyPair':
            key_pair = data['keyPair']
    return cert_arn, cert_pem, key_pair

def register_taxi_in_db(taxi_data):
    response = lambda_client.invoke(
        FunctionName=REGISTER_LAMBDA_ARN,
        InvocationType='RequestResponse',
        Payload=json.dumps(taxi_data)
    )
    return response

def register_taxi_in_iot(taxi_id):
    response = iot_client.create_thing(
        thingName=taxi_id,
        thingTypeName=IOT_THING_TYPE
    )
    resp = iot_client.add_thing_to_thing_group(
        thingName=taxi_id,
        thingGroupName=IOT_THING_GROUP
    )
    cert_arn, cert_pem, key_pair = create_certificate()
    resp = iot_client.attach_policy(
        policyName=IOT_POLICY,
        target=cert_arn
    )
    resp = iot_client.attach_thing_principal(
        thingName=taxi_id,
        principal=cert_arn
    )
    return cert_arn, cert_pem, key_pair

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
    taxi_data = json.loads(json.loads(payload.decode('utf-8')).get("body"))
    print(taxi_data)
    cert_arn, cert_pem, key_pair = register_taxi_in_iot(taxi_data["taxi_id"])

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Taxi registered successfully",
            "taxi_data": taxi_data,
            "cert_pem": cert_pem,
            "priv_key": key_pair['PrivateKey'],
        }),
    }

