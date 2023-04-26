import requests
import json
import asyncio

class RegistrationSimulator:
    "Manages registration of taxis through API"
    "This is required only for simulation purpose"
    "A real taxi owner is supposed to visit the registration"
    "site and downloadload the certificate after registration"

    def __init__(self, end_point=""):
        self.end_point = end_point
        if not end_point:
            self.end_point = "https://h6x05weali.execute-api.us-east-1.amazonaws.com/Prod/register_taxi/"


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

if __name__ == '__main__':

    def register_async():
        registration_sim = RegistrationSimulator()
        data = requests.get("https://randomuser.me/api/").json()
        email = data.get("results")[0].get("email")
        name = data.get("results")[0].get("name")
        taxi_class = "Deluxe"
        registration = registration_sim.create_registration(email, name["first"], name["last"], taxi_class)
        registration.register()

    ntaxis = 0
    while True:
        ans = input("No of taxis to simulate: ")
        try:
            ntaxis = int(ans)
            break
        except:
            print("Invalid entry, try again!.")

    print("Registering taxis")
    tasks = []
    for i in range(ntaxis):
        #tasks.append(asyncio.create_task(register_async()))
        register_async()
    #asyncio.gather(*tasks)

