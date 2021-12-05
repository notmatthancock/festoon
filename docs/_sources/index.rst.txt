festoon
-------

:code:`festoon` is a collection of Python decorators for common tasks. This includes things like:

- logging when a function was called and return (optionally logging the arguments and return value)
- logging the runtime of a function
- automatically substituting environment variables for arguments
- adding variables to docstrings

.. automodule:: festoon 

logit
=====
.. autofunction:: logit

.. autodata:: festoon.logging_tools.FMTCALL_TYPE
.. autodata:: festoon.logging_tools.FMTEXCP_TYPE
.. autodata:: festoon.logging_tools.FMTDONE_TYPE

timeit
======
.. autofunction:: timeit

.. autodata:: festoon.logging_tools.FMTTIME_TYPE

fromenv
=======
.. autofunction:: fromenv

docfill
=======
.. autofunction:: docfill

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
