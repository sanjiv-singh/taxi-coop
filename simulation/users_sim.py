import random
import requests
import boto3
import asyncio

AWS_API_GATEWAY = boto3.client('apigateway')

def get_api_endpoints():
    resp = AWS_API_GATEWAY.get_rest_apis()
    try:
        api_id = resp.get("items")[0]["id"]
        return f"https://{api_id}.execute-api.us-east-1.amazonaws.com/Prod/users/", \
            f"https://{api_id}.execute-api.us-east-1.amazonaws.com/Prod/request-ride"
    except:
        print("Error: API Gateway not found")
        print("cannot proceed further")
        import sys; sys.exit(1)

USERS_END_POINT, REQUEST_RIDE_END_POINT = get_api_endpoints()

def fetch_users(end_point):
    return requests.get(end_point).json()

def create_random_location(south_west, north_east):
    lat = random.uniform(south_west[0], north_east[0])
    lng = random.uniform(south_west[1], north_east[1])
    return f"{lat},{lng}"

async def request_ride(user):
    data = {
        "user_id": user.get("user_id"),
        "taxi_class": random.choice([0, 1, 2]),
        "origin": create_random_location((12.8, 77.5), (13.5, 78.2)),
        "destination": create_random_location((12.8, 77.5), (13.5, 78.2)),
    }
    response = requests.post(REQUEST_RIDE_END_POINT, json=data).json()
    print(response)

async def main(users):

    tasks = []
    for user in users:
        tasks.append(asyncio.create_task(request_ride(user)))
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

