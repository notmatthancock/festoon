import inspect
import itertools
import logging
import functools
import time
import traceback
from typing import Any, Callable, NamedTuple, Optional, Union


class _KwargItem(NamedTuple):
    name: str
    value: Any


def _fn_name(fn: Callable) -> str:
    try:
        return fn.__qualname__
    except AttributeError:
        return fn.__name__


def format_call(fn: Callable, args: tuple, kwargs: dict) -> str:
    params = inspect.signature(fn).parameters
    sentinel = object()
    kwarg_items = [_KwargItem(k, v) for k, v in kwargs.items()]
    result = []
    for (name, param), input_item in itertools.zip_longest(
        params.items(),
        [*args, *kwarg_items],
        fillvalue=sentinel,
    ):
        if input_item is sentinel:
            value = param.default
        elif name == "self":  # HACK
            continue
        elif isinstance(input_item, _KwargItem):
            value = input_item.value
        else:
            value = input_item
        result.append(f"{name}={value}")
    paramstr = ", ".join(result)
    return f"CALL {_fn_name(fn)}({paramstr})"


def format_excp(fn: Callable, excp: Exception) -> str:
    return f"EXCP {_fn_name(fn)}\n{traceback.format_exc()}"


def format_done(fn: Callable, output: Any) -> str:
    return f"DONE {_fn_name(fn)}->{output}"


def format_time(
    fn: Callable,
    seconds: float,
    fmtstr: str = "{seconds:.2f}s"
) -> str:
    result = "TIME {_fn_name(fn)} "
    result += fmtstr
    return eval("f'"+result+"'")  # eval bad, yea yea


#: Type signature of :code:`fmtcall` option of :code:`logit` decorator. The
#: call formatter accepts the function that was decorated and the
#: (\*args, \*\*kwargs) tuple and dict used to invoke the function. The return
#: from the formatter should be a string used in the log message.
FMTCALL_TYPE = Callable[[Callable, tuple, dict], str]
#: Type signature of :code:`fmtexcp` option of :code:`logit` decorator
FMTEXCP_TYPE = Callable[[Callable, Exception], str]
#: Type signature of :code:`fmtdone` option of :code:`logit` decorator. The
#: formatter takes as input the decorated function and the value returned
#: from the call. The return is a string used for the log message.
FMTDONE_TYPE = Callable[[Callable, Any], str]

#: Type signature of :code:`fmttime` option :code:`timeit` decorator.
FMTTIME_TYPE = Callable[[Callable, float], str]


def logit(
    fn: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    level: int = logging.INFO,
    fmtcall: Optional[FMTCALL_TYPE] = format_call,
    fmtexcp: Optional[FMTEXCP_TYPE] = format_excp,
    fmtdone: Optional[FMTDONE_TYPE] = format_done,
):
    """Log a function on call, exception, and return

    Note:
        This is not a mathematical logit function :)

    Args:
        fn: function to be decorated
        name: name of logger to use. If None, then fn.__module__ will be used.
        level: logging level. Default is logging.INFO.
        fmtcall: a callable that formats the inputs used to invoke `fn`. If
            None, then no logging call is made before function invokation.
        fmtexcp: a callable that formats exception if one is raised when
            invoking `fn`. If None, then no logging called is made.
        fmtdone: a callable that formats the data returned by invoking `fn`.
            If None, then no logging call is made on the returned data.

    Examples:
        The default settings add a logging statement when the function
        is invoked (CALL) and completed (DONE). The inputs to the function
        are logged on call and the result returned by the function is
        logged on done:

        >>> @logit
        >>> def func(x, y=2):
        >>>     return x+y
        >>> logging.basicConfg(level=logging.INFO)
        >>> func(1)
        # INFO.__main__: CALL func(x=1, y=2)
        # INFO.__main__: DONE func->3

        The contents of log messages are controlled by providing format
        functions to the decorator. A value of :code:`None` produces no
        log message for the respective stage:

        >>> @logit(fmtdone=None)
        >>> def func(x, y=2):
        >>>     return x+y
        >>> logging.basicConfig(level=logging.INFO)
        >>> func(1)
        # INFO.__main__: CALL func(x=1, y=2)

        If a class member function is decorated, the default logging formatters
        will automatically prefix the class name in logging statements:

        >>> class Foo:
        >>>     @logit
        >>>     def func(self, x, y=2):
        >>>         return x+y
        >>> logging.basicConfg(level=logging.INFO)
        >>> Foo().func(1)
        # INFO.__main__: CALL Foo.func(x=1, y=2)
        # INFO.__main__: DONE Foo.func->3
    """

    # Allows @logit or @logit(...)
    if fn is None:
        return functools.partial(
            logit,
            name=name,
            level=level,
            fmtcall=fmtcall,
            fmtexcp=fmtexcp,
            fmtdone=fmtdone,
        )

    if not callable(fn):
        raise ValueError(f"{fn} is not callable")

    name = name or fn.__module__

    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        logger = logging.getLogger(name)
        result = no_result_flag = object()
        try:
            if fmtcall:
                msg = fmtcall(fn, args, kwargs)
                logger.log(level, msg)
            result = fn(*args, **kwargs)
        except Exception as e:
            if fmtexcp:
                logger.log(level, fmtexcp(fn, e))
            raise e
        finally:
            if fmtdone and result is not no_result_flag:
                msg = fmtdone(fn, result)
                logger.log(level, msg)
        return result

    return wrapped


def timeit(
    fn: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    level: Optional[int] = logging.INFO,
    fmttime: Union[FMTTIME_TYPE, str] = format_time,
):
    """Log time ellapsed by this function

    Args:
        fn: function to be decorated
        name: name of logger to use. If None, then fn.__module__ will be used.
        level: logging level. Default is logging.INFO.
        fmttime: fmttime can either be a function or a format string. If it
            is a function, then it should accept (fn: Callable, seconds: float)
            and return a message string. If `fmttime` is a string, then it
            should be a format string with argument "seconds". See examples
            below

    Examples:

        The default settings produce a log message at level info with
        the ellapsed number of seconds taken by the decorated function:

        >>> @timeit
        >>> def func():
        >>>     import time
        >>>     time.sleep(0.75)
        >>> func()
        # INFO:__main__:TIME func 0.75s

        A format string can be used to customize the log message:

        >>> @timeit(fmttime="{seconds*1000:.0f} milliseconds")
        >>> def func():
        >>>     import time
        >>>     time.sleep(0.75)
        >>> func()
        # INFO:__main__:TIME func 751 milliseconds

        Or a callable can be used to customize the log message:

        >>> @timeit(fmttime=lambda fn, s: f"{fn.__name__} took {s} seconds!")
        >>> def func():
        >>>     import time
        >>>     time.sleep(0.75)
        >>> func()
        # INFO:__main__:func took 0.7508368770004381 seconds!

    """

    # Allows @timeit or @timeit(...)
    if fn is None:
        return functools.partial(
            timeit,
            name=name,
            level=level,
            fmttime=fmttime,
        )

    if not callable(fn):
        raise ValueError(f"{fn} is not callable")

    if isinstance(fmttime, str):
        fmttime = functools.partial(format_time, fmtstr=fmttime)

    name = name or fn.__module__

    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        logger = logging.getLogger(name)
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        stop = time.perf_counter()
        logger.log(level, fmttime(fn, stop-start))
        return result

    return wrapped


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    @timeit(fmttime=lambda fn, s: f"{fn.__name__} took {s} seconds!")
    def func():
        import time
        time.sleep(0.75)

    func()
