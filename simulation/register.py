import requests
import json
import asyncio
import random
import boto3

AWS_API_GATEWAY = boto3.client('apigateway')


def read_taxis(path: str):
    with open(path, "r") as f:
        return json.load(f)

class RegistrationSimulator:
    "Manages registration of taxis through API"
    "This is required only for simulation purpose"
    "A real taxi owner is supposed to visit the registration"
    "site and downloadload the certificate after registration"

    def __init__(self, end_point=""):
        self.end_point = end_point
        if not end_point:
            resp = AWS_API_GATEWAY.get_rest_apis()
            try:
                api_id = resp.get("items")[0]["id"]
                self.end_point = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/Prod/taxis/"
            except:
                print("Error: API Gateway not found")
                print("cannot proceed with registration")
                import sys; sys.exit(1)


    def create_registration(self, email, first_name, last_name, taxi_class):
        self.taxi_data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "taxi_class": taxi_class
        }
        return self

    def register(self):
        data = requests.post(self.end_point, json=self.taxi_data).json()
        taxi_id = data.get("taxi_data").get("taxi_id")
        print("Taxi registered with id: ", taxi_id)
        with open(f".certs/{taxi_id}.pem", "w+") as cert_file:
            cert_file.write(data.get("cert_pem"))
        with open(f".certs/{taxi_id}.private.key", "w+") as key_file:
            key_file.write(data.get("priv_key"))

def register_async(taxi):
    registration_sim = RegistrationSimulator()
    registration = registration_sim.create_registration(**taxi)
    registration.register()

def main():
    ntaxis = 0
    sample_taxis = read_taxis("sample_taxis.json")
    while True:
        ans = input("No of taxis to register: ")
        try:
            ntaxis = int(ans)
            if ntaxis < 0:
                print("Invalid entry, try again!.")
                continue
            if ntaxis == 0:
                print("No taxis to register, exiting.")
                import sys; sys.exit(0)
            if ntaxis > len(sample_taxis):
                print("Not enough sample data, try again!.")
                continue
            break
        except:
            print("Invalid entry, try again!.")

    print(f"Registering taxis")
    tasks = []
    for taxi in sample_taxis[:ntaxis]:
        register_async(taxi)


if __name__ == '__main__':
    main()
