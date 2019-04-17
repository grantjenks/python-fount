"""Proof-of-concept web framework for creating single-page applications.

Command for live-reloading:

    $ adev runserver fount/apps/demo.py -p 8080

"""

import aiohttp
import json
import asyncio
from aiohttp import web


class DemoPage:
    def __init__(self, ws):
        self.ws = ws
        self.seconds = 0
        self.clicked = 0

    async def update(self):
        doc = self.content()
        message = json.dumps(doc)
        await self.ws.send_str(message)

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


INDEX = '''<!doctype html>
<html>
  <head>
    <title>Live Page Prototype</title>
    <script src="https://unpkg.com/react@16/umd/react.development.js" crossorigin></script>
    <script src="https://unpkg.com/react-dom@16/umd/react-dom.development.js" crossorigin></script>
  </head>
  <body>
    <div id="root">
    </div>
    <script>
     function clicker() {
         socket.send('clicked');
     }

     function convert(value) {
         if (typeof value === 'string' || value instanceof String) {
             return value;
         }
         else if (value instanceof Array) {
             return value.map(convert);
         }
         if (value['tag'] == 'button' && value['props']['type'] == 'button') {
             value['props']['onClick'] = clicker;
         }
         return React.createElement(
             value['tag'],
             value['props'],
             convert(value['children'])
         );
     }

     var socket = new WebSocket('ws://127.0.0.1:8080/socket');
     socket.onmessage = function (event) {
         var message = JSON.parse(event.data);
         var element = convert(message);
         ReactDOM.render(element, document.getElementById('root'));
     };
    </script>
  </body>
</html>
'''


async def index(request):
    return web.Response(text=INDEX, content_type='text/html')


app = web.Application()
app.add_routes([
    web.get('/', index),
    web.get('/socket', websocket_handler)
])


if __name__ == '__main__':
    web.run_app(app)
