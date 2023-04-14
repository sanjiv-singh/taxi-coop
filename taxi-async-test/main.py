import asyncio
from taxi import Taxi




async def main():
    taxi = Taxi()
    print('Created new taxi')
    t1 = asyncio.create_task(taxi._drive())
    t2 = asyncio.create_task(taxi._report())
    await asyncio.gather(t1, t2)


if __name__ == '__main__':
    asyncio.run(main())