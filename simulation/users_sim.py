import random
import requests
import json
import boto3
import asyncio

AWS_API_GATEWAY = boto3.client('apigateway')
TAXI_LIMIT = 3

def get_api_endpoints():
    resp = AWS_API_GATEWAY.get_rest_apis()
    try:
        api_id = resp.get("items")[0]["id"]
        return f"https://{api_id}.execute-api.us-east-1.amazonaws.com/Prod/users/", \
            f"https://{api_id}.execute-api.us-east-1.amazonaws.com/Prod/taxis/request/", \
            f"https://{api_id}.execute-api.us-east-1.amazonaws.com/Prod/rides/", \
            f"https://{api_id}.execute-api.us-east-1.amazonaws.com/Prod/taxis/book/"
    except:
        print("Error: API Gateway not found")
        print("cannot proceed further")
        import sys; sys.exit(1)

USERS_END_POINT, REQUEST_RIDE_END_POINT, RIDES_END_POINT, BOOK_RIDE_END_POINT = get_api_endpoints()

def fetch_users(end_point):
    return requests.get(end_point).json()

def create_random_location(south_west, north_east):
    lat = random.uniform(south_west[0], north_east[0])
    lng = random.uniform(south_west[1], north_east[1])
    return f"{lat},{lng}"

def select_taxi(taxis):
    for taxi in taxis:
        taxi["timestamp"] = datetime.strptime(taxi["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")
    return min(taxis, key=lambda x: x["timestamp"])

async def request_ride(data):
    ride_data = requests.post(REQUEST_RIDE_END_POINT, json=data).json()
    ride_id = ride_data.get("ride_id")
    if not ride_id:
        print("Error: Ride request failed")
        return
    print(f'Ride request created with ride_id: {ride_id}')
    print("Waiting for taxi to accept the ride request")
    while True:
        await asyncio.sleep(2)
        rides = requests.get(f"{RIDES_END_POINT}{ride_id}").json()
        try:
            accepted_taxis = rides[0].get("accepted_taxis")
            if len(accepted_taxis) > 0:
                break
        except:
            pass
    print(accepted_taxis)
    selected_taxi = select_taxi(accepted_taxis)
    return selected_taxi.get("taxi_id")
    import sys; sys.exit()
    taxi_ids = [taxi.get("_id") for taxi in response.get("nearest_taxis") if taxi.get("_id") is not None]
    if len(taxi_ids) == 0:
        print("No taxi available")
        return
    return random.choice(taxi_ids)


async def book_ride(user):
    data = {
        "user_id": user.get("_id"),
        "taxi_class": random.choice([0, 1, 2, 3]),
        "origin": create_random_location((12.8, 77.5), (13.5, 78.2)),
        "destination": create_random_location((12.8, 77.5), (13.5, 78.2)),
        "taxi_limit": TAXI_LIMIT
    }
    taxi_id = await request_ride(data)
    if taxi_id is None:
        return
    data["taxi_id"] = taxi_id
    response = requests.post(BOOK_RIDE_END_POINT,
                             json=data).json()
    print(response)
    return None

async def main(users):

    tasks = []
    for user in users:
        tasks.append(asyncio.create_task(book_ride(user)))
    await asyncio.gather(*tasks)

if __name__ == '__main__':

    users = fetch_users(USERS_END_POINT)
    nusers = len(users)
    if nusers == 0:
        print("No user registered. Please register users first.")
        import sys; sys.exit()
    while True:
        ans = input("No of users to simulate: ")
        try:
            n = int(ans)
            if nusers < n:
                print("Not enough users registered")
                continue
            users = users[:n]
            break
        except:
            print("Invalid entry, try again!.")

    asyncio.run(main(users))

