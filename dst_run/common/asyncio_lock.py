import asyncio
from functools import wraps


__all__ = ['lock']

_lock = asyncio.Lock()


def lock(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        await _lock.acquire()
        res = await f(*args, **kwargs)
        _lock.release()
        return res
    return wrapper
