import os
import json
import requests
import asyncio
import boto3

AWS_API_GATEWAY = boto3.client('apigateway')

def get_api_endpoint():
    resp = AWS_API_GATEWAY.get_rest_apis()
    try:
        api_id = resp.get("items")[0]["id"]
        return f"https://{api_id}.execute-api.us-east-1.amazonaws.com/Prod/users/"
    except:
        print("Error: API Gateway not found")
        print("cannot proceed further")
        import sys; sys.exit(1)

API_END_POINT = get_api_endpoint()

def read_users(path: str):
    with open(path, "r") as f:
        return json.load(f)


async def register_user(user):
    data = requests.post(API_END_POINT, json=user).json()
    user_id = data.get("user_id")
    print("User registered with id: ", user_id)


async def main():


    nusers = 0
    sample_users = read_users("sample_users.json")
    while True:
        ans = input("No of users to register (max 15): ")
        try:
            nusers = int(ans)
            if nusers < 0:
                print("Invalid entry, try again!.")
                continue
            if nusers == 0:
                print("No users to register, exiting.")
                import sys; sys.exit(0)
            if nusers > len(sample_users):
                print("Not enough sample data, try again!.")
                continue
            break
        except:
            print("Invalid entry, try again!.")
    tasks = []
    for user in sample_users[:nusers]:
        tasks.append(asyncio.create_task(register_user(user)))
    await asyncio.gather(*tasks)

if __name__ == '__main__':

    asyncio.run(main())

