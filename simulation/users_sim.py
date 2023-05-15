import random
import requests
import boto3
import asyncio
from datetime import datetime

AWS_API_GATEWAY = boto3.client('apigateway')

def parse_isodatetime(datetime_str):
    try:
        return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%f%z")
    except ValueError:
        # Perhaps the datetime has a whole number of seconds with no decimal
        # point. In that case, this will work:
        return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S%z")

def get_api_endpoints():
    resp = AWS_API_GATEWAY.get_rest_apis()
    try:
        api_id = resp.get("items")[0]["id"]
        return f"https://{api_id}.execute-api.us-east-1.amazonaws.com/Prod/users/", \
            f"https://{api_id}.execute-api.us-east-1.amazonaws.com/Prod/taxis/request", \
            f"https://{api_id}.execute-api.us-east-1.amazonaws.com/Prod/rides", \
            f"https://{api_id}.execute-api.us-east-1.amazonaws.com/Prod/taxis/book"
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

class User:

    def __init__(self, **user_data):
        self.user_id = user_data.get("_id")
        self.first_name = user_data.get("first_name")
        self.last_name = user_data.get("last_name")
        self.email = user_data.get("email")


    async def request_ride(self):
        response = requests.post(REQUEST_RIDE_END_POINT, json=self.data).json()
        self.ride_id = response.get("ride_id")
        print(f'Requested ride with id {self.ride_id}')
        accepted_taxis = []
        while True:
            await asyncio.sleep(2)
            url = f'{RIDES_END_POINT}/{self.ride_id}/'
            try:
                ride = requests.get(url).json()
                accepted_taxis = ride.get("accepted_taxis")
                if accepted_taxis:
                    break
            except:
                print("No taxis yet. Waiting..")
        print(f'{len(accepted_taxis)} accepted the request')
        # Select taxi that responded first
        taxi_timings = [{"taxi_id": taxi["taxi_id"], "timing": parse_isodatetime(
            taxi["timestamp"]["$date"])} for taxi in accepted_taxis]
        sorted_taxis = sorted(taxi_timings, key=lambda x: x["timing"])
        return sorted_taxis[0]["taxi_id"]


    async def book_ride(self):
        self.data = {}
        self.data['user_id'] = self.user_id
        self.data['taxi_class'] = random.choice([0, 1, 2, 3])
        self.data['origin'] = create_random_location((12.8, 77.5), (13.5, 78.2))
        self.data['destination'] = create_random_location((12.8, 77.5), (13.5, 78.2))
        self.data['taxi_limit'] = 3

        self.taxi_id = await self.request_ride()
        if self.taxi_id is None:
            return
        self.data["taxi_id"] = self.taxi_id
        self.data["ride_id"] = self.ride_id
        print(f'Taxi {self.taxi_id} responded first')
        response = requests.post(BOOK_RIDE_END_POINT,
                                json=self.data).json()
        if response.get("message") == 'updated succesfully':
            print(f'Taxi {self.taxi_id} booked')
        response = requests.patch(f'{RIDES_END_POINT}/{self.ride_id}/',
                        data={"booked_taxi": self.taxi_id, "status": "BOOKED"}).json()
        return None

async def main(users):

    tasks = []
    for user in users:
        user_obj = User(**user)
        #tasks.append(asyncio.create_task(book_ride(user)))
        tasks.append(asyncio.create_task(user_obj.book_ride()))
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

