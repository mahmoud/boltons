
import inspect

from boltons.funcutils import wraps, FunctionBuilder


def test_wraps_async():
    # from https://github.com/mahmoud/boltons/issues/194
    import asyncio

    def delayed(func):
        @wraps(func)
        async def wrapped(*args, **kw):
            await asyncio.sleep(1.0)
            return await func(*args, **kw)

        return wrapped


    async def f():
        await asyncio.sleep(0.1)

    assert asyncio.iscoroutinefunction(f)

    f2 = delayed(f)

    assert asyncio.iscoroutinefunction(f2)
