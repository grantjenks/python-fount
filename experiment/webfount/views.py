import asyncio, httpx, json, urllib.parse
from django.http import (
    HttpRequest, HttpResponse, StreamingHttpResponse, Http404, JsonResponse
)
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.urls import path, re_path
from .relay import *

BACKEND = "http://127.0.0.1:5000"

BOOTSTRAP_TEMPLATE = """
<base href="/proxy/">      <!-- ensure form/action re‑routes hit the proxy -->
<script src="https://unpkg.com/htmx.org@1.9.12"></script>
<script src="https://unpkg.com/diff-match-patch"></script>
<script src="https://unpkg.com/morphdom@2.6.1/dist/morphdom-umd.min.js"></script>
<script>
(function() {{
    const dmp = new diff_match_patch;
    const es  = new EventSource("/sse/{sid}");
    es.addEventListener("patch", ev => {{
        const patch = dmp.patch_fromText(ev.data);
        const newHtml = dmp.patch_apply(patch, document.documentElement.outerHTML)[0];
        morphdom(document.documentElement, newHtml);
    }});
}})();
</script>
"""


def inject_bootstrap(html: str, sid: str) -> str:
    """
    Add <base> and client‑side SSE boot code (htmx + diff‑match‑patch + morphdom).
    """
    bootstrap = BOOTSTRAP_TEMPLATE.format(sid=sid)
    head_end = html.find("</head>")
    return html[:head_end] + bootstrap + html[head_end:]


async def fetch_backend(method: str, path: str, data=None):
    url = urllib.parse.urljoin(BACKEND + "/", path.lstrip("/"))
    async with httpx.AsyncClient() as c:
        resp = await c.request(method, url, data=data)
        resp.raise_for_status()
        return resp.text


def make_sse_frame(patch: str):
    return f"event: patch\ndata: {patch.replace(chr(10), '\\n')}\n\n"


@csrf_exempt
async def proxy_entry(request: HttpRequest, path: str = ""):
    # session id: cookie or new
    sid = request.COOKIES.get("SID") or await new_session()
    prev_html = await load_page(sid) or ""

    if request.method == "POST":
        body = await request.body
        data = urllib.parse.parse_qs(body.decode())
        new_html = await fetch_backend("POST", path, data=data)
    else:
        new_html = await fetch_backend("GET", path)

    # diff & store
    diff = dmp.diff_main(prev_html, new_html)
    if diff:
        dmp.diff_cleanupSemantic(diff)
    patch = dmp.patch_make(prev_html, new_html, diff)
    patch_txt = dmp.patch_toText(patch)
    await save_page(sid, new_html)
    if patch_txt:
        # push to own SSE queue; shared rooms handled elsewhere
        await push_patch(sid, make_sse_frame(patch_txt))

    # initial bootstrap for first load
    if not prev_html:
        new_html = inject_bootstrap(new_html, sid)

    resp = HttpResponse(new_html)
    resp.set_cookie("SID", sid)
    return resp


async def sse_stream(request: HttpRequest, sid: str):
    if request.headers.get("accept") != "text/event-stream":
        raise Http404()

    async def event_stream():
        async for patch in pop_patches(sid):
            yield patch

    return StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
    )


async def admin_sessions(request: HttpRequest):
    # simple JSON list
    keys = await redis.keys(PAGE_KEY.format(sid="*"))
    sids = [k.split(":")[1] for k in keys]
    return JsonResponse({"sessions": sids})


async def admin_edit(request: HttpRequest, sid: str):
    html = await load_page(sid)
    if html is None:
        raise Http404()

    if request.method == "POST":
        new_html = (await request.body).decode()
        diff = dmp.diff_main(html, new_html)
        dmp.diff_cleanupSemantic(diff)
        patch = dmp.patch_make(html, new_html, diff)
        patch_txt = dmp.patch_toText(patch)
        await save_page(sid, new_html)
        await push_patch(sid, make_sse_frame(patch_txt))
        return HttpResponse("patched")

    # GET => editable page
    editable = (
        "<!doctype html><title>Admin edit</title>"
        "<h1>Editing session {sid}</h1>"
        "<div id='editor' contenteditable='true' style='border:1px solid'>"
        f"{html}"
        "</div>"
        """
        <script>
        const ed = document.getElementById("editor");
        let timeout;
        ed.addEventListener("input", _=>{
            clearTimeout(timeout);
            timeout = setTimeout(()=>{
                fetch("", {method:"POST", body:ed.innerHTML});
            }, 500);
        });
        </script>
        """
    )
    return HttpResponse(editable)


async def create_room(request: HttpRequest):
    """POST /api/room -> {"room_id": "..."}"""
    if request.method != "POST":
        raise Http404()
    room_id = await new_session()
    await redis.sadd("rooms", room_id)
    return JsonResponse({"room_id": room_id})


async def join_room(request: HttpRequest, room: str):
    """User joins a room by aliasing his SID’s queue to the room queue."""
    sid = request.COOKIES.get("SID") or await new_session()
    await redis.sadd(f"room:{room}", sid)
    # no response body needed
    return HttpResponse("ok")
