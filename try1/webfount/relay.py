import asyncio, json, uuid, os
import redis.asyncio as aioredis
from django.conf import settings
from diff_match_patch import diff_match_patch

dmp = diff_match_patch()
redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

PAGE_KEY   = "page:{sid}"          # raw html snapshot
QUEUE_KEY  = "queue:{sid}"         # list acts as SSE queue
SESSION_TTL = 60 * 60              # expire in 1 h


async def new_session():
    sid = uuid.uuid4().hex
    return sid


async def save_page(sid: str, html: str):
    await redis.set(PAGE_KEY.format(sid=sid), html, ex=SESSION_TTL)


async def load_page(sid: str) -> str | None:
    return await redis.get(PAGE_KEY.format(sid=sid))


async def push_patch(sid: str, patch: str):
    await redis.rpush(QUEUE_KEY.format(sid=sid), patch)


async def pop_patches(sid: str):
    """Blocking pop for StreamingHttpResponse."""
    while True:
        _, patch = await redis.blpop(QUEUE_KEY.format(sid=sid), timeout=300)
        yield patch + "\n\n"     # SSE frames already formatted
