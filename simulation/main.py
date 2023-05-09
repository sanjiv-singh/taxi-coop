import os
import asyncio
from register import RegistrationSimulator
from taxi_system import TaxiFactory

PUBLISH_INTERVAL = 5


async def main(taxis):

    taxi_factory = TaxiFactory()

    tasks = []
    for taxi_id in taxis:
        taxi = taxi_factory.create_taxi(taxi_id)
        taxi.connect()
        taxi.subscribe()
        tasks.append(asyncio.create_task(taxi.main_loop(PUBLISH_INTERVAL)))
        tasks.append(asyncio.create_task(taxi.taxi_loop()))
    await asyncio.gather(*tasks)

if __name__ == '__main__':

    taxis = []
    for name in os.listdir('.certs/'):
        if name.endswith('.private.key'):
            taxis.append(name[:-12])
    ntaxis = len(taxis)
    if ntaxis == 0:
        print("No taxi registered. Please register taxis first.")
        import sys; sys.exit()
    while True:
        ans = input("No of taxis to simulate: ")
        try:
            n = int(ans)
            if ntaxis < n:
                print("Not enough taxis registered")
                continue
            taxis = taxis[:n]
            break
        except:
            print("Invalid entry, try again!.")

    asyncio.run(main(taxis))

