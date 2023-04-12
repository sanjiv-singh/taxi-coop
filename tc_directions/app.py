import json

import requests

key='***REMOVED***'
directions_url = 'https://maps.googleapis.com/maps/api/directions' #/json?origin=Toronto&destination=Montreal&avoid=highways&mode=bicycling&key=YOUR_API_KEY"
output_format = 'json'


def handle_get(event):
    origin = event["queryStringParameters"]["origin"]
    destination = event["queryStringParameters"]["destination"]
    url = f'{directions_url}/{output_format}?origin={origin}&destination={destination}&mode=driving&key={key}'
    response = requests.get(url).json()
    address = response["directions"]["routes"][0]["legs"][0]["steps"]
    print(address)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "directions": response,
        }),
    }

def handle_post(event):
    body = json.loads(event["body"])
    origin = body["origin"]
    destination = body["destination"]
    url = f'{directions_url}/{output_format}?origin={origin}&destination={destination}&mode=driving&key={key}'
    response = requests.get(url).json()
    print(response)
    steps = response["routes"][0]["legs"][0]["steps"]
    print(steps)
    #location = response["results"][0]["geometry"]["location"]

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

