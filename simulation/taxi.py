import asyncio
from mqtt import MQTTClient
from configuration import ConfigurationManager

from enum import Enum
import random
import json
import requests
import asyncio
import datetime
import time
from bson.objectid import ObjectId

DIST_FACTOR = 111139    # meters per degree of lat/long
DELAY = 2               # Delay inseconds between each computation cycle (must be less than Publish rate)


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
    """Creates a random location within the given bounds"""
    lat = random.uniform(south_west[0], north_east[0])
    lng = random.uniform(south_west[1], north_east[1])
    return [lat, lng]

def clean_data(data):
    """Converts the data received from the MQTT broker into appropriate float values"""
    if 'origin' in data:
        data['origin'] = [float(x) for x in data['origin'].split(',')]
    if 'destination' in data:
        data['destination'] = [float(x) for x in data['destination'].split(',')]
    return data

class Taxi(MQTTClient):
    """Taxi class that represents a taxi device"""

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
        self._subscribe(f'{self._topic}/{self._taxi_id}/+', callback=self._on_message)
    
    async def publish(self):
        """Publishes the taxi data to designated topic"""
        data = {}
        data['taxi_id'] = self._taxi_id
        data['taxi_class'] = self._taxi_class
        data['status'] = self._status
        data['location'] = self._location
        data['timestamp'] = str(datetime.datetime.now())
        self._publish_data(self._topic, data)

    def _on_message(self, client, userdata, msg):
        """Callback function for MQTT client
        Handles the messages received from the broker"""

        # Extract the data from the message mayload
        data = clean_data(json.loads(msg.payload))

        # Act based on the topic and status of the taxi
        if msg.topic == f'{self._topic}/{self._taxi_id}/request' and self._status == TaxiStatus.AVL:
            print(f"\nTaxi {self._taxi_id} received request for ride {data['ride_id']} with user {data['user_id']}")
            time.sleep(random.uniform(0.1, 0.4))
            self._accept_ride(data)

        if msg.topic == f'{self._topic}/{self._taxi_id}/book' and self._status == TaxiStatus.AVL:
            self._status = TaxiStatus.BOOKED
            print(f"\nTaxi {self._taxi_id} booked for user {data['user_id']}")

        # Set taxi attributes based on the data received
        for key, value in data.items():
            setattr(self, f'_{key}', value)


    def _accept_ride(self, data):
        """Accepts the ride request and updates the ride status"""
        accept_url = f'https://{self._config.api_id}.execute-api.us-east-1.amazonaws.com/Prod/rides/accept/'
        response = requests.post(
                accept_url,
                json={
                    "taxi_id": self._taxi_id,
                    "ride_id": data.get("ride_id")
                }
        ).json()
    
    async def _commence_ride(self):
        """Updates the ride status to IN_PROGRESS and records the trip start time"""

        rides_url = f'https://{self._config.api_id}.execute-api.us-east-1.amazonaws.com/Prod/rides/'
        response = requests.patch(
                rides_url + self._ride_id,
                data={
                    "start_time": datetime.datetime.now().isoformat(),
                    "status": 'IN_PROGRESS'
                }
        ).json()

    async def _complete_ride(self):
        """Updates the ride status to COMPLETED and records the trip end time"""

        rides_url = f'https://{self._config.api_id}.execute-api.us-east-1.amazonaws.com/Prod/rides/'
        response = requests.patch(
                rides_url + self._ride_id,
                data={
                    "end_time": datetime.datetime.now().isoformat(),
                    "status": 'COMPLETED'
                }
        ).json()
        delattr(self, '_ride_id')

    async def taxi_loop(self):
        """Act based on the status of the taxi"""

        while True:

            if self._status == TaxiStatus.BOOKED:
                # If status is booked, the taxi is yet to reach the origin
                # hence drive to the origin
                print(f"\nTaxi booked, going to origin {self._origin}")
                await self._drive((self._lat, self._lng), self._origin, 30)

                # Once the taxi reaches the origin, commence the ride
                await self._commence_ride()
                self._status = TaxiStatus.TRIP

            elif self._status == TaxiStatus.AVL:
                # If status is available, the taxi is free to take a ride
                # It can just sleep for a while and continue waiting
                # or it can drive to a random location
                await asyncio.sleep(DELAY)
                #await self._drive((self._lat, self._lng), create_random_location((12.8, 77.5), (13.5, 78.2)), 10)

            elif self._status == TaxiStatus.TRIP:
                # If status is trip, the taxi is on a ride
                # so it should drive to the destination
                print(f"\n{self._taxi_id} on trip, going to destination {self._destination}")
                await self._drive((self._lat, self._lng), self._destination, 30)

                # Once the taxi reaches the destination, complete the ride
                print(f"\nArrived at destination {self._destination}, {self._taxi_id} available for booking.")
                await self._complete_ride()
                self._status = TaxiStatus.AVL

            else:

                # If status is unknown, the taxi should not do anything
                await asyncio.sleep(DELAY)


    async def _drive(self, origin, destination, speed):
        """Implements the driving logic for the taxi"""

        lat_dist = (destination[0] - origin[0])
        lng_dist = (destination[1] - origin[1])
        
        # Calculate the distance between origin and destination in degrees sqrt(x2 + y2)
        distance_in_degrees = (lat_dist**2 + lng_dist**2)**0.5
        
        # Convert difference in northings and eastings to meters
        distance = distance_in_degrees * DIST_FACTOR

        # Calculate time taken to travel the distance
        time = distance/speed
        print(f"\nDistance: {distance/1000.0}Km, Time: {time/60.0}min")

        # Calculate the no of steps, this is required as we have a sleep interval
        steps = int(time/DELAY) + 1
        print(f"No of steps: {steps}")

        # Pre calculate the array of lats and longs based on steps
        lats = [origin[0] + (lat_dist/steps)*i for i in range(steps)]
        lngs = [origin[1] + (lng_dist/steps)*i for i in range(steps)]

        # For every step update the location based on lat longs calculated earlier
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
    
