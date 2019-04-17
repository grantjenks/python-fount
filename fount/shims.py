"""Shims for Web Frameworks

"""

from aiohttp import web

def make_aiohttp_handler(page_factory):
    def websocket_handler(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        page = page_factory()
        await page.connect(ws)
        return ws

    return websocket_handler
