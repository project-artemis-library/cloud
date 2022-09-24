from datetime import datetime
from time import sleep
from typing import AnyStr, Callable, Optional
from urllib.request import Request, urlopen

from logger import MyLogger

logger = MyLogger(__name__)


@logger.logging_function(with_arg=True, write_log=True)
def http_get(url: str) -> AnyStr:
    req = Request(
        url=url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        },
    )
    resp = urlopen(req)
    return resp.read()


def generate_get_http_client(sec_interval: int) -> Callable[[str], AnyStr]:
    dt_prev: Optional[datetime] = None

    def process(url: str) -> AnyStr:
        nonlocal dt_prev
        if dt_prev is not None:
            sec_sleep: float = 0
            delta = datetime.now() - dt_prev
            if sec_interval - delta.total_seconds() > 0:
                sec_sleep = sec_interval - delta.total_seconds()
            sleep(sec_sleep)

        result = http_get(url)
        dt_prev = datetime.now()
        return result

    return process
