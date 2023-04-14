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

class Taxi:

    def __init__(self):
        self._uuid = uuid4()
        self._taxi_class = TaxiClass.DELUXE
        self._status = TaxiStatus.AVL
        self._location = create_random_location((12.8, 77.5), (13.5, 78.2))
        self._start = time.perf_counter()
        self._elapsed_time = self._start
    
    async def _drive(self):
        while True:
            await asyncio.sleep(random.uniform(0.2, 2.0))
            self._location[0] += random.uniform(-0.1, 0.1)
            self._location[1] += random.uniform(-0.1, 0.1)
            print('...', end='|', flush=True)
    
    async def _report(self):
        while True:
            t1 = asyncio.sleep(5)
            t2 = self._log()
            await asyncio.gather(t1, t2)
    
    async def _log(self):
        print('')
        print(self._location)
        self._elapsed_time = time.perf_counter() - self._start
        print(f'Elapsed time = {self._elapsed_time}')

