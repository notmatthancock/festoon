from typing import Callable, Optional


def docfill(
    *args,
    template: Optional[str] = None,
    **kwargs
):
    """Format the decorated function's docstring using given args and kwargs

    This is useful if some functions share many common inputs or if the
    range of valid values for a parameter is specified by some global constant.

    Notes:
        - If a template string is provided, then args and kwargs are
          formatted into this string to produce the decorated
          function's docstring
        - If no template string is provided and the decorated function's
          docstring is not None, then this docstring is formatted with the
          given args and kwargs.

    Args:
        args: values to be formatted in docstring as positional arguments,
            e.g., {0}, {1}, etc.
        kwargs: values to be formatted in docstring as keyword arguments,
            e.g, {some_var}, {the_value}, etc.
        template: string to use as template for decorated function's docstring

    Examples:

        >>> @docfill([1, 2, 42], valid_animals={"cat", "dog"})
        >>> def func(numbers, animals):
        >>>     \"\"\"This is a function
        >>>     Args:
        >>>         numbers: options are {0}
        >>>         animals: valid choices are {valid_animals}
        >>>     \"\"\"
        >>> help(func)
        Help on function func in module __main__:
        func(numbers, animals)
            This is a function
            Args:
                numbers: options are [1, 2, 42]
                animals: valid choices are {'dog', 'cat'}

    """
    def decorator(fn: Callable) -> Callable:
        if template is not None:
            fn.__doc__ = template
        if fn.__doc__ is not None:
            fn.__doc__ = fn.__doc__.format(*args, **kwargs)
        return fn
    return decorator


@docfill([1, 2, 42], valid_animals={"cat", "dog"})
def func(numbers, animals):
    """This is a function
    Args:
        numbers: options are {0}
        animals: valid choices are {valid_animals}
    """
