from configuration import ConfigurationManager
import boto3
from uuid import uuid4

from taxi import Taxi

AllowedActions = ['both', 'publish', 'subscribe']

AWS_IOT_CLIENT = boto3.client('iot')

class TaxiFactory:

    def __init__(self, ) -> None:
        self._config = ConfigurationManager("config.json")
        #self._client = config_manager.create_client()

    def create_taxi(self):
        taxi = Taxi(self._config)
        return taxi

