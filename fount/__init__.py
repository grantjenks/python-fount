"""Fount

Web framework for creating single-page applications.

Design ideas:

  - Use asyncio.Queue for incoming messages.
  - One page should support multiple connected websockets.
  - Render a page once then broadcast to all connected websockets.
  - Run a page by consuming messages from queue.
  - Trigger updates at 60 FPS as needed.

How to handle scale?

  * Ultimately this is just PUB/SUB  with an HTML model.
  * There should be optimizations for 60 FPS.

"""

import abc
import aiohttp
import json
import asyncio
from aiohttp import web


class Fount:
    @classmethod
    async def create(cls):
        self = cls()
        self.queue = asyncio.Queue()
        self.pipes = set()

    async def connect(self, pipe):
        self.pipes.add(pipe)

    async def receive(self, message):
        await self.queue.put(message)

    async def disconnect(self, pipe):
        self.pipes.remove(pipe)

    async def destroy(self):
        pass

    async def send(self, message):
        pass  # TODO: broadcast

    async def run(self):
        pass  # TODO: process messages in queue

    async def render(self):
        pass  # TODO: generate json
    

class DemoPage(Page):
    def __init__(self, ws):
        self.ws = ws
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

    async def update(self):
        doc = self.content()
        message = json.dumps(doc)
        await self.ws.send_str(message)

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


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([web.get('/socket', websocket_handler)])
    web.run_app(app)


__title__ = 'fount'
__version__ = '0.1.0'
__build__ = 0x000100
__author__ = 'Grant Jenks'
__copyright__ = '2019, Grant Jenks'
__license__ = 'Apache 2.0'
