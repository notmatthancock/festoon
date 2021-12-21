# `festoon`

`festoon` ([read the full docs here](https://notmatthancock.github.io/festoon/)) is a collection of useful Python decorators for common tasks.

Here's an example that retries a function on failures:

```python
from festoon import retry

@retry(schedule=[1, 2, 8, 32], catch=ConnectionError)
def flaky_function():
    ...
```
    

Here's a concrete logging example:

```python
from festoon import logit

@logit
def func(x, y=2, z="something else"):
    return x+y

if __name__ == "__main__":
    import logging
    logging.basicConfg(level=logging.INFO)
    func(1)
    # INFO.__main__: CALL func(x=1, y=2, z="something else")
    # INFO.__main__: DONE func->3
```
Notice that implicit default parameters are logged when using the default call formatter function.

Here is an example to inject variables into a docstring:

```python
from festoon import docfill

LOW = 0.5
HIGH = 0.75
ANIMAL_CHOICES = ("dog", "cat", "ostrich")

@docfill(LOW, HIGH, animals=ANIMAL_CHOICES)
def func(threshold: float, animal: str):
    """Do a thing

    Args:
        threshold: a value between {0:.2f} and {1:.2f}
        animal: valid options are {animals}
    """
    ...


if __name__ == "__main__":
    help(func)
    # Help on function func in module __main__:
    # 
    # func(threshold: float, animal: str)
    #     Do a thing
    # 
    #     Args:
    #         threshold: a value between 0.50 and 0.75
    #         animal: valid options are ('dog', 'cat', 'ostrich')
```
