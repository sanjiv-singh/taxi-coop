import asyncio
from mqtt import MQTTClient
from configuration import ConfigurationManager

from enum import Enum
from uuid import uuid4
import random
import asyncio
import datetime
from bson.objectid import ObjectId

DIST_FACTOR = 111139  # meters per degree of lat/long
DELAY = 2


class TaxiClass(int, Enum):
    DELUXE = 0
    LUXARY = 1
    UTILITY = 2

class TaxiStatus(int, Enum):
    NAVL = 0
    AVL = 1
    BOOKED = 2
    TRIP = 3

def create_random_location(south_west, north_east):
    lat = random.uniform(south_west[0], north_east[0])
    lng = random.uniform(south_west[1], north_east[1])
    return [lat, lng]

class Taxi(MQTTClient):

    def __init__(self, config: ConfigurationManager, taxi_id, taxi_class=TaxiClass.DELUXE):
        self._config = config
        self._taxi_id = taxi_id
        self._topic = self._config.topicRoot
        self._taxi_class = taxi_class
        self._status = TaxiStatus.AVL
        self._lat, self._lng = create_random_location((12.8, 77.5), (13.5, 78.2))
        super(Taxi, self).__init__()

    @property
    def _location(self):
        return {
                "type": "Point",
                "coordinates": [self._lng, self._lat]
        }
    
    def connect(self):
        self._connect()
    
    def disconnect(self):
        self._disconnect()
    
    def subscribe(self):
        self._subscribe(f'{self._topic}/{self._taxi_id}', callback=self._on_message)
    
    async def publish(self):
        data = {}
        data['taxi_id'] = self._taxi_id
        data['taxi_class'] = self._taxi_class
        data['status'] = self._status
        data['location'] = self._location
        data['timestamp'] = str(datetime.datetime.now())
        self._publish_data(self._topic, data)

    def _on_message(self, client, userdata, msg):
        print(f"Message received: {msg.payload}")
    
    async def _keep_doing_trips(self):
        while True:
            print("New Trip")
            await self.do_trip()

    async def do_trip(self,
            origin=create_random_location((12.8, 77.5), (13.5, 78.2)),
            destination=create_random_location((12.8, 77.5), (13.5, 78.2))):
        print(f"Doing trip from {origin} to {destination}")
        # Set status to booked
        self._status = TaxiStatus.BOOKED
        # Drive to origin
        print("Driving to origin")
        await self._drive((self._lat, self._lng), origin, 20)
        # Set status to trip
        self._status = TaxiStatus.TRIP
        # Drive to destination
        print("Driving to destination")
        await self._drive(origin, destination, 20)
        # Set status to available
        self._status = TaxiStatus.AVL

    async def _drive(self, origin, destination, speed):
        # Convert difference in northings and eastings to meters
        #x, y = (destination[1] - origin[1])*DIST_FACTOR, (destination[0] - origin[0])*DIST_FACTOR
        # Calculate distance between origin and destination
        lat_dist = (destination[0] - origin[0])
        lng_dist = (destination[1] - origin[1])
        distance_in_degrees = (lat_dist**2 + lng_dist**2)**0.5
        distance = distance_in_degrees * DIST_FACTOR
        # Calculate time taken to travel the distance
        time = distance/speed
        print(f"Distance: {distance}m, Time: {time}s")
        # Calculate the no of steps
        steps = int(time/DELAY) + 1
        # Pre calculate the array of lats and longs based on steps
        lats = [origin[0] + (lat_dist/steps)*i for i in range(steps)]
        lngs = [origin[1] + (lng_dist/steps)*i for i in range(steps)]
        for i in range(steps):
            try:
                await asyncio.sleep(DELAY)
                self._lat = lats[i]
                self._lng = lngs[i]
            except KeyboardInterrupt:
                break

    async def main_loop(self, delay):
        while True:
            try:
                await asyncio.sleep(delay)
                await self.publish()
            except KeyboardInterrupt:
                break

        print("Closing connection ..")
        self.disconnect()
        print("Connection closed.")
    
