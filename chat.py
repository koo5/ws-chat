import asyncio
import datetime
import json
import aiohttp
from aiohttp import web


routes = web.RouteTableDef()
websockets = set()
history = []

@routes.get('/', name='hello')
async def hello(request):
        with open('home.html', 'rb') as f:
            return web.Response(
                body=f.read().decode('utf8'),
                content_type='text/html')


@routes.post('/')
async def login(request):
    form_data = await request.post()

    name = form_data.get('name')
    if name:
        return web.HTTPFound(request.app.router['chat'].url_for(name=name))
    else:
        return web.HTTPFound(request.app.router['hello'].url_for())


@routes.get('/{name}/', name='chat')
async def chat_page(request):
    with open('chat.html', 'rb') as f:
        return web.Response(
            body=f.read().decode('utf8'),
            content_type='text/html')


async def snd(ws,x):
    if isinstance(x, str):
        await ws.send_str(x)
    else:
        await ws.send_json(x)


@routes.get('/{name}/ws/')
async def websocket(request):
    name = request.match_info['name']
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    await send_to_all('system', f'{name} joined!')
    for text in list(history):
        await snd(ws,text)
    websockets.add(ws)

    try:
        async for msg in ws:
            if msg.type in [aiohttp.WSMsgType.TEXT]:
                await send_to_all_json(json.loads(msg.data))
                #await send_to_all(name, msg.data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' %
                    ws.exception())
    finally:
        websockets.remove(ws)

    await send_to_all('system', f'{name} left')

    return ws


async def send_to_all(name, message):
    now = datetime.datetime.now()
    text = f'{now:%H:%M:%S} – {name}: {message}'
    await send_to_all_raw(text)

async def send_to_all_raw(text):
    history.append(text)
    if len(history) > 20:
        del history[:10]

    tasks = set()
    for ws in websockets:
        tasks.add(asyncio.create_task(ws.send_str(text)))
    while tasks:
        done, tasks = await asyncio.wait(tasks)

async def send_to_all_json(text):
    history.append(text)
    if len(history) > 20:
        del history[:10]

    tasks = set()
    for ws in websockets:
        tasks.add(asyncio.create_task(ws.send_json(text)))
    while tasks:
        done, tasks = await asyncio.wait(tasks)


def get_app(argv=None):
    app = web.Application()
    app.add_routes(routes)
    return app

if __name__ == '__main__':
    app = get_app()
    web.run_app(app)
