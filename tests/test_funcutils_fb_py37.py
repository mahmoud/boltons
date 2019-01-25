
import time
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

    # from https://github.com/mahmoud/boltons/pull/195
    def yolo():
        def make_time_decorator(wrapped):
            @wraps(wrapped)
            async def decorator(*args, **kw):
                return (await wrapped(*args, **kw))
            return decorator

        return make_time_decorator


    @yolo()
    async def foo(x):
        await asyncio.sleep(x)

    start_time = time.monotonic()
    asyncio.run(foo(0.3))
    duration = time.monotonic() - start_time

    assert duration > 0.3
