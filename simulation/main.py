import os
import asyncio
from register import RegistrationSimulator
from taxi_system import TaxiFactory

PUBLISH_INTERVAL = 2


async def main(taxis):

    taxi_factory = TaxiFactory()

    tasks = []
    for taxi_id in taxis:
        taxi = taxi_factory.create_taxi(taxi_id)
        taxi.connect()
        taxi.subscribe()
        tasks.append(asyncio.create_task(taxi.main_loop(PUBLISH_INTERVAL)))
        tasks.append(asyncio.create_task(taxi._drive()))
    await asyncio.gather(*tasks)

if __name__ == '__main__':

    taxis = []
    for name in os.listdir('.certs/'):
        if name.endswith('.private.key'):
            taxis.append(name[:-12])
    asyncio.run(main(taxis))

