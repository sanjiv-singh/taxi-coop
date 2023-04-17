import asyncio
from mqtt import MQTTClient
from configuration import ConfigurationManager

from enum import Enum
from uuid import uuid4
import random
import asyncio
import time


class TaxiClass(Enum):
    DELUXE = 0
    LUXARY = 1
    UTILITY = 2

class TaxiStatus(Enum):
    NAVL = 0
    AVL = 1
    BOOKED = 2
    TRIP = 3

def create_random_location(south_west, north_east):
    lat = random.uniform(south_west[0], north_east[0])
    lng = random.uniform(south_west[1], north_east[1])
    return [lat, lng]

class Taxi(MQTTClient):

    def __init__(self, config: ConfigurationManager):
        self._config = config
        self._taxi_id = str(uuid4())
        self._topic = self._config.topicRoot
        self._taxi_class = TaxiClass.DELUXE
        self._status = TaxiStatus.AVL
        self._lat, self._lng = create_random_location((12.8, 77.5), (13.5, 78.2))
        self._start = time.perf_counter()
        self._elapsed_time = self._start
        self._data = dict(id=str(self._taxi_id), lat=self._lat, lng=self._lng)
        super(Taxi, self).__init__()
    
    def connect(self):
        self._connect()
    
    def subscribe(self):
        self._subscribe(f'{self._topic}/{self._taxi_id}')
    
    def get_data(self):
        return self._data
    
    async def _drive(self):
        while True:
            try:
                await asyncio.sleep(random.uniform(0.2, 2.0))
                self._lat += random.uniform(-0.1, 0.1)
                self._lng += random.uniform(-0.1, 0.1)
                self._data['lat'] = self._lat
                self._data['lng'] = self._lng
            except KeyboardInterrupt:
                break

    
