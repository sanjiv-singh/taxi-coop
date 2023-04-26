from configuration import ConfigurationManager
import boto3
import random

from taxi import Taxi, TaxiClass

AWS_IOT_CLIENT = boto3.client('iot')

class TaxiFactory:

    def __init__(self) -> None:
        self._config = ConfigurationManager("config.json")

    def create_taxi(self, taxi_id):
        taxi = Taxi(self._config, taxi_id, random.randint(0, 2))
        return taxi

