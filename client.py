import datetime
import os
import time
from pathlib import Path

import aiofiles as aiofiles
import aiohttp

import asyncio


async def create(number):
    data = {
        "org_name": "sampleName",
        "date": "21.04.2023",
        "product_list": [[f"Product{number}", 1, number*10]]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8080/add_item", json=data) as res:
            return await res.json()
        # для полностью однопоточного
        '''async with aiofiles.open(Path(os.getcwd(), "downloaded", f'result{number}.xlsx'), 'wb') as file:
                await file.write(await res.read())'''


async def get_monitoring():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8080/queue_info") as res:
            js = await res.json()
            for element in js:
                print(js[element])


async def get_file(num):
    data = {'id': num}
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8080/get_file", json=data) as res:
            async with aiofiles.open(Path(os.getcwd(), "downloaded", f'{data["id"]}.xlsx'), 'wb') as file:
                await file.write(await res.read())

            print(res)


async def main():
    tasks = []
    '''for number in range(5):
        tasks.append(asyncio.create_task(create(number)))
    result = await asyncio.gather(*tasks)'''
    for number in range(15):
        tasks.append(asyncio.create_task(create(number)))
    result = await asyncio.gather(*tasks)
    tasks.clear()
    for res in result:
        tasks.append(asyncio.create_task(get_file(res["id"])))
    result = await asyncio.gather(*tasks)
    print(result)



asyncio.run(main())
