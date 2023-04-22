import json
import os
import requests

BASE_URL = 'https://maps.googleapis.com/maps/api/directions'
OUTPUT_FORMAT = 'json'
SOUTHWEST = os.environ['SOUTHWEST']
NORTHEAST = os.environ['NORTHEAST']


def handle_get(event):
    key = event["queryStringParameters"]["key"]
    origin = event["queryStringParameters"]["origin"]
    destination = event["queryStringParameters"]["destination"]
    url = f'{BASE_URL}/{OUTPUT_FORMAT}?origin={origin}&destination={destination}&mode=driving&key={key}'
    response = requests.get(url).json()
    steps = response["routes"][0]["legs"][0]["steps"]

    return {
        "statusCode": 200,
        "body": json.dumps({
            "directions": steps,
        }),
    }

def handle_post(event):
    key = event["queryStringParameters"]["key"]
    body = json.loads(event["body"])
    origin = body["origin"]
    destination = body["destination"]
    url = f'{BASE_URL}/{OUTPUT_FORMAT}?origin={origin}&destination={destination}&mode=driving&key={key}'
    response = requests.get(url).json()
    steps = response["routes"][0]["legs"][0]["steps"]

    return {
        "statusCode": 200,
        "body": json.dumps({
            "directions": steps,
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
    else:
        return handle_default(event)

