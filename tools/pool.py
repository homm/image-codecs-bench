import sys
import os.path
from collections import deque
from concurrent.futures import Future, ThreadPoolExecutor
from itertools import islice


CONCURRENCY = 6
QUEUE_SIZE = CONCURRENCY * 5


pool = ThreadPoolExecutor(CONCURRENCY)


def _consume_futures(futures, keep=0):
    while len(futures) > keep:
        future = futures.popleft()
        if not isinstance(future, Future):
            yield future
            continue

        try:
            if future.result():
                yield future.result()
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f'{fname}:{exc_tb.tb_lineno} {exc_type.__name__}: {exc_obj}')


def iterate_futures(fn):
    def inner(it, *args, **kwargs):
        futures = deque()
        consumed = False
        it = fn(it, *args, **kwargs)
        while not consumed:
            consumed = True
            for future in islice(it, QUEUE_SIZE):
                consumed = False
                futures.append(future)
            yield from _consume_futures(futures, QUEUE_SIZE)
        yield from _consume_futures(futures)
    return inner


def enrich_result(fn, *more_result):
    def inner(*args, **kwargs):
        result = fn(*args, **kwargs)
        if result is None:
            return None
        if type(result) is not tuple:
            result = (result,)
        return more_result + result
    return inner
