import asyncio
import sys
import json
import aiohttp


async def send_one(msg):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('http://localhost:8080/CLI/ws') as ws:
            await ws.send_json({"found-ap":{"SSID":"DIRECT-7sWorkCentre 3225","channel":11,"RSSI":-72,"encType":4,"BSSID":"9E:93:4E:44:C6:A5"}})
            await ws.send_json({"found-ap":{"SSID":"DIRE111","channel":11,"RSSI":-2,"encType":4,"BSSID":"9E:93:4E:45:C6:A5"}})

asyncio.run(send_one(' '.join(sys.argv[1:])))
