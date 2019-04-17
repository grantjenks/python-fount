"""Clock Web Application

"""

import time
import asyncio

from aiohttp import web
from ..shims import make_aiohttp_handler

app = web.Application()

class ClockPage(Page):
    async def setup(self):
        ticker = asyncio.create_task(self.tick())
        return ticker

    async def tick(self):
        while True:
            await self.update()
            secs = time.time()
            delay = 1 - (secs - int(secs))
            await asyncio.sleep(delay)

    def render(self):
        return f'<p>The current time is {time.strftime("%X")}.</p>'

index = '''<!doctype html>
<html>
  <head>
    <title>Clock Web Application</title>
  </head>
  <body>
    <h1>Clock Web Application</h1>
    <div id="clock"></div>
    <script src="https://unpkg.com/react@16/umd/react.development.js"
            crossorigin></script>
    <script src="https://unpkg.com/react-dom@16/umd/react-dom.development.js"
            crossorigin></script>
    <script src="/fount.js"></script>
    <script>
      var clock = document.getElementById("clock");
      Fount.connect(clock, "ws://127.0.0.1:8000/fount/");
    </script>
  </body>
</html>'''

with open('fount.js') as reader:
    fount_js = reader.read()

app.add_routes([
    web.get('/', lambda req: index),
    web.get('/fount.js', lambda req: fount_js),
    web.get('/fount/', make_aiohttp_handler(ClockPage)),
])

if __name__ == '__main__':
    web.run_app(app)
