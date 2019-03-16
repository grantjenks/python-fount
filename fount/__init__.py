"""Proof-of-concept Server for Live Web Pages

$ adev runserver server.py -p 8080

"""

import aiohttp
import json
import asyncio
from aiohttp import web

async def hello(request):
    return web.Response(text="Hello, world")

app = web.Application()
app.add_routes([web.get('/', hello)])


class Page:
    def __init__(self, ws):
        self.ws = ws

    async def update(self):
        doc = self.content()
        message = json.dumps(doc)
        await self.ws.send_str(message)

    def content(self):
        raise NotImplementedError


class DemoPage(Page):
    def __init__(self, ws):
        super().__init__(ws)
        self.seconds = 0
        self.clicked = 0

    async def run(self):
        await self.update()
        ticker = asyncio.create_task(self.tick())
        async for message in self.ws:
            assert message.type == aiohttp.WSMsgType.TEXT
            assert message.data == 'clicked'
            self.clicked += 1
            await self.update()
        ticker.cancel()

    async def tick(self):
        while True:
            await asyncio.sleep(1)
            self.seconds += 1
            await self.update()

    def content(self):
        return [
            {'tag': 'h1', 'props': {'key': 0}, 'children': 'Live Page Demo'},
            {'tag': 'div', 'props': {'key': 1}, 'children': [
                {
                    'tag': 'p',
                    'props': {'key': 0},
                    'children': f'Seconds: {self.seconds}',
                },
            ]},
            {
                'tag': 'button',
                'props': {'key': 2, 'type': 'button'},
                'children': 'click me!',
            },
            {
                'tag': 'p',
                'props': {'key': 3},
                'children': f'Clicked: {self.clicked}',
            },
        ]


async def websocket_handler(request):

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    page = DemoPage(ws)
    await page.run()

    return ws

app.add_routes([web.get('/socket', websocket_handler)])


if __name__ == '__main__':
    web.run_app(app)
