import asyncio
import sys
import json
import aiohttp


async def send_one(msg):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('http://localhost:8080/CLI/ws') as ws:
            await ws.send_json(json.loads(msg))

asyncio.run(send_one(' '.join(sys.argv[1:])))
