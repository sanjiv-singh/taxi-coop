import json
import os
import requests
import boto3

SOUTHWEST = os.environ['SOUTHWEST']
NORTHEAST = os.environ['NORTHEAST']

QUERY_LAMBDA_ARN = os.environ['query_lambda_arn']

lambda_client = boto3.client('lambda')
iot_client = boto3.client('iot-data')


def report_error(error):
    return {
        "statusCode": 500,
        "body": json.dumps({
            "message": f"Error: {error}"
        })
    }


def query_db(query, limit):
    response = lambda_client.invoke(
        FunctionName=QUERY_LAMBDA_ARN,
        InvocationType='RequestResponse',
        Payload=json.dumps(dict(query=query, limit=limit))
    )
    return response

def notify_taxis(taxis, origin, destination, user_id, ride_id):
    data = dict(user_id=user_id, origin=origin, destination=destination, ride_id=ride_id)
    payload = json.dumps(data).encode('utf8')
    responses = []
    for taxi in taxis:
        taxi_id = taxi["_id"]
        print(f'Notifying taxi {taxi_id}')
        response = iot_client.publish(
            topic=f'iot/TAXI/{taxi_id}/request',
            qos=1,
            payload=payload 
        )
        responses.append(response)
    return responses


def lambda_handler(event, context):

    body = json.loads(event["body"])
    print(body)
    taxi_class = body["taxi_class"]
    origin = [float(coord) for coord in body["origin"].split(',')]
    origin.reverse()
    destination = [float(coord) for coord in body["destination"].split(',')]
    destination.reverse()
    user_id = body.get("user_id")
    taxi_limit = body.get("taxi_limit")

    # Contruct a mongodb location query
    print('######################## CUSTOMER LOCATION ########################')
    start_location =  { '$geometry': { 
            "type": "Point", 'coordinates': origin 
        }
    }
    print(start_location)   

    # Getting the nearest taxis to a customer
    # Find the nearest taxis that are available and are of requested class
    print('########################  NEAREST TAXIS ########################')
    nearest_query = {'location': {"$near":  start_location}, 'status': 1}

    # If the customer has requested a specific taxi class, then add that to the query
    # Ignore the taxi class if the customer has not requested a specific class (taxi_class = 3)
    if int(taxi_class) < 3:
        nearest_query['taxi_class'] = taxi_class

    # Query the database for the nearest taxis
    response = query_db(nearest_query, taxi_limit)
    payload = response["Payload"].read()   
    nearest_taxis = json.loads(json.loads(payload.decode('utf-8')).get("body"))
    print(nearest_taxis)

    # Create a new ride record in the database
    host = event["headers"]["Host"]
    path = event["requestContext"]["path"]
    path = path.replace('taxis/request', 'rides')
    data = {
        "origin": {
            "type": "Point",
            'coordinates': origin
        },
        "destination": {
            "type": "Point",
            'coordinates': destination
        },
        "taxi_class": taxi_class,
        "status": "REQUESTED",
        "accepted_taxis": [],
        "user_id": user_id
    }

    # Send the request to the rides API
    url = f'https://{host}{path}'
    print(url)
    print(data)
    response = requests.post(url, json=data).json()
    print(response)

    # Notify the nearest taxis about the ride request
    ride_id = response.get("ride_id")
    responses = notify_taxis(nearest_taxis,
                        body["origin"], body["destination"], user_id, ride_id)
    print(responses)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "ride_id": ride_id,
        }),
    }
