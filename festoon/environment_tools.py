import functools
import inspect
import os
from typing import Any, Callable, get_args, List, Optional


def _cast(value: Any, param: inspect.Parameter) -> Any:

    types = set()

    if param.annotation is not param.empty:
        types.add(param.annotation)
        for t in get_args(param.annotation):
            types.add(t)
    if param.default is not param.empty:
        types.add(type(param.default))

    for Type in types:
        try:
            return Type(value)
        except Exception:
            pass
    return value


def fromenv(
    fn: Optional[Callable] = None,
    prefix: Optional[str] = None,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
):
    """Allow any keyword argument to be supplied by an environment variable

    Notes:
        If a keyword argument has type annotations, then variable will
        be attempted to be cast as the respective type if it is read
        from the environment.


    Args:
        fn: callable to be decorated
        prefix: name to use as a prefix for supplied environment variables.
            For example, if the decorated function has a keyword argument
            "table_name" and prefix="DB", then the table_name argument
            may be set via the environment variable "DB_TABLE_NAME". If None,
            then the prefix is set to the decorated function's name in
            all caps.
        include: only include these listed parameter names for substitution
        exclude: list of paramters names to ignore

    Examples:

        Let's define a function in :code:`main.py`::

            @fromenv
            def func(x: int = 0, y: int = 42):
                return x + y

            if __name__ == "__main__":
                result = func()
                print(result)

        Then, we can run :code:`main.py`::

            $ FUNC_X=100 python main.py
            142
            $ FUNC_X=100 FUNC_Y=-1 python main.py
            99

        Now let's use a different prefix and add excludes::

            @fromenv(prefix="FOO", excludes=["y"])
            def func(x: int = 0, y: int = 42):
                return x + y

            if __name__ == "__main__":
                result = func()
                print(result)

        Now, running looks like as follows::

            $ FOO_X=100 python main.py
            142
            $ FOO_X=100 FOO_Y=-1 python main.py
            142

        Note that in the second execution, FOO_Y=-1 has no effect because
        "y" was in the excludes list.
    """
    if fn is None:
        return functools.partial(
            fromenv,
            prefix=prefix,
            include=include,
            exclude=exclude,
        )

    if not callable(fn):
        raise ValueError(f"{fn} must be callable")

    if prefix is None:
        prefix = fn.__name__.upper()

    if not prefix.endswith("_"):
        prefix = prefix + "_"

    @functools.wraps(fn)
    def wrapped(*args, **kwargs):

        parameters = inspect.signature(fn).parameters

        for name, param in parameters.items():
            if (
                name in kwargs or
                param.default is param.empty or
                (exclude is not None and name in exclude) or
                (include is not None and name not in include)
            ):
                continue

            # Try to get the value from the environment
            env_name = f"{prefix}{name.upper()}"
            try:
                value = os.environ[env_name]
            except KeyError:
                continue

            # Try to cast the value as annotation type if it has one
            value = _cast(value, param)

            kwargs[name] = _cast(value, param)

        return fn(*args, **kwargs)

    return wrapped


if __name__ == "__main__":
    from typing import Union

    @fromenv
    def func(a, b: Union[float, int] = None, c=42):
        return a + b + c

    result = func(1)
    print(result)
