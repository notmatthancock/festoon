import functools
import logging
import time
from typing import Callable, List, Optional, Type, Union


LOG = logging.getLogger(__name__)


def retry(
    fn: Optional[Callable] = None,
    *,
    schedule: Optional[List[int]] = None,
    catch: Union[Type[Exception], List[Type[Exception]]] = Exception,
    log_exceptions: bool = True,
):
    """Repeatedly retry a function on exception after sleeping

    Args:
        fn: callable being decorated
        schedule: sequence of delay times to sleep in between call attempts
        catch: Exception class or list of Exception classes that are caught
            when invoking the decoratee.
        log_exceptions: If True, then logging.exception is called whenever
            an error is caught.

    Examples:
        >>> count = 0
        >>>
        >>> @retry
        >>> def func():
        >>>     global count
        >>>     if count == 2:
        >>>         return "SUCCESS!"
        >>>     else:
        >>>         count += 1
        >>>         raise Exception
        >>>
        >>> print(func())
        # ERROR:__main__:
        # Traceback (most recent call last):
        # ...
        # INFO:__main__:Sleeping for 1 seconds and then retrying...
        # ERROR:__main__:
        # Traceback (most recent call last):
        # ...
        # INFO:__main__:Sleeping for 2 seconds and then retrying...
        # SUCCESS!

    """
    # Allows @retry or @retry(...)
    if fn is None:
        return functools.partial(
            retry,
            schedule=schedule,
            catch=catch,
            log_exceptions=log_exceptions,
        )

    if not callable(fn):
        raise ValueError(f"{fn} is not callable")

    if issubclass(catch, Exception):
        catch = (catch,)

    if schedule is None:
        schedule = [2**p for p in range(7)]

    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        for delay in schedule:
            try:
                return fn(*args, **kwargs)
            except tuple(catch) as e:
                if log_exceptions:
                    LOG.exception(e)
                LOG.info(f"Sleeping for {delay} seconds and then retrying...")
                time.sleep(delay)
        # Last chance: no try except safety net!
        return fn(*args, **kwargs)

    return wrapped


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    count = 0

    @retry()
    def func():
        global count
        if count == 2:
            return "SUCCESS!"
        else:
            count += 1
            raise IOError

    result = func()
    print(result)
