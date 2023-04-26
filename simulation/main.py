import asyncio
from register import RegistrationSimluator
from taxi_system import TaxiFactory

PUBLISH_INTERVAL = 2


async def main(ntaxis):

    taxi_factory = TaxiFactory()

    tasks = []
    for _ in range(ntaxis):
        taxi = taxi_factory.create_taxi()
        taxi.connect()
        taxi.subscribe()
        tasks.append(asyncio.create_task(taxi.main_loop(PUBLISH_INTERVAL)))
        tasks.append(asyncio.create_task(taxi._drive()))
    await asyncio.gather(*tasks)

if __name__ == '__main__':

    registration_sim = RegistrationSimluator(
        ""
    )
    ntaxis = 0
    while True:
        ans = input("No of taxis to simulate: ")
        try:
            ntaxis = int(ans)
            break
        except:
            print("Invalid entry, try again!.")

    print("Registering taxis")
    for i in range(ntaxis):
        data = requests.get("https://randomuser.me/api/").json()
        email = data.get("email")
        name = data.get("name")
        taxi_class = "Deluxe"
        taxi = registration_sim.create_taxi(email, name["first"], name["last"], taxi_class)
        taxi.register()

    print("Starting simulation")
    #asyncio.run(main(ntaxis))

