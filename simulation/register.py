import requests
import json

class RegistrationSimluator:
    "Manages registration of taxis through API"
    "This is required only for simulation purpose"
    "A real taxi owner is supposed to visit the registration"
    "site and downloadload the certificate after registration"

    def init(self, api_endpoint):
        self.end_point = api_endpoint

    def create_taxi(self, email, first_name, last_name, taxi_class):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.taxi_class = taxi_class

    def register(self):
        taxi_data  ={
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "taxi_class": self.taxi_class
        }
        status, message = requests.post(self.end_point, json=taxi_data)
        if int(status) != 200:
            print("failed to register taxi")
            return {}
        message_json = json.loads(message)
        taxi_id = message_json.get("taxi_data").get("taxi_id")
        with open(f".certs/{taxi_id}.pem") as cert_file:
            cert_file.write(message_json.get("cert"))
        with open(f".certs/{taxi_id}.private.key") as key_file:
            key_file.write(message_json.get("key"))
