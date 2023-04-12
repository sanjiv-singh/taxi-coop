import json
import os
import requests

BASE_URL = 'https://maps.googleapis.com/maps/api/geocode'
OUTPUT_FORMAT = 'json'
SOUTHWEST = os.environ['SOUTHWEST']
NORTHEAST = os.environ['NORTHEAST']


def handle_get(event):
    key = event["queryStringParameters"]["key"]
    lat = event["queryStringParameters"]["lat"]
    lng = event["queryStringParameters"]["lng"]
    url = f'{BASE_URL}/{OUTPUT_FORMAT}?latlng={lat},{lng}&key={key}'
    response = requests.get(url).json()
    address = response["results"][0]["formatted_address"]

    return {
        "statusCode": 200,
        "body": json.dumps({
            "address": address,
        }),
    }

def handle_post(event):
    key = event["queryStringParameters"]["key"]
    address = json.loads(event["body"])["address"]
    url = f'{BASE_URL}/{OUTPUT_FORMAT}?address={address}&key={key}'
    response = requests.get(url).json()
    location = response["results"][0]["geometry"]["location"]

    return {
        "statusCode": 200,
        "body": json.dumps({
            "location": location,
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

