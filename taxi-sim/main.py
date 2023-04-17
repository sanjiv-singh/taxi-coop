import asyncio
from taxi_system import TaxiFactory

PUBLISH_INTERVAL = 0.1


async def main():

    taxi_factory = TaxiFactory()

    tasks = []
    for _ in range(10):
        taxi = taxi_factory.create_taxi()
        taxi.connect()
        taxi.subscribe()
        tasks.append(asyncio.create_task(taxi.main_loop(PUBLISH_INTERVAL)))
        tasks.append(asyncio.create_task(taxi._drive()))
    await asyncio.gather(*tasks)

if __name__ == '__main__':

    asyncio.run(main())

