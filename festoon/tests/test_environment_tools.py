from contextlib import contextmanager
import os
from typing import Any, Dict
import unittest

from festoon.environment_tools import fromenv


@contextmanager
def _temp_env(variables: Dict[str, Any]):
    for k, v in variables.items():
        os.environ[k] = str(v)
    try:
        yield
    finally:
        for k in variables:
            os.environ.pop(k)


class TestLogit(unittest.TestCase):
    def test_fromenv_basic(self):
        @fromenv
        def func(x: int = 0, y: int = 42):
            return x + y

        with self.subTest("set x from env"):
            with _temp_env({"FUNC_X": 100}):
                result = func()
            self.assertEqual(142, result)

        with self.subTest("set x and y from env"):
            with _temp_env({"FUNC_X": 100, "FUNC_Y": -1}):
                result = func()
            self.assertEqual(99, result)

    def test_fromenv_prefix(self):
        @fromenv(prefix="FOO")
        def func(x: int = 0, y: int = 42):
            return x + y

        with self.subTest("set x from env"):
            with _temp_env({"FOO_X": 100}):
                result = func()
            self.assertEqual(142, result)

        with self.subTest("set x and y from env"):
            with _temp_env({"FOO_X": 100, "FOO_Y": -1}):
                result = func()
            self.assertEqual(99, result)

    def test_fromenv_include(self):
        @fromenv(include=["y"])
        def func(x: int = 0, y: int = 42):
            return x + y

        with self.subTest("set x from env"):
            with _temp_env({"FUNC_X": 100}):
                result = func()
            self.assertEqual(42, result)

        with self.subTest("set x and y from env"):
            with _temp_env({"FUNC_X": 100, "FUNC_Y": -1}):
                result = func()
            self.assertEqual(-1, result)

    def test_fromenv_exclude(self):
        @fromenv(exclude=["y"])
        def func(x: int = 0, y: int = 42):
            return x + y

        with self.subTest("set x from env"):
            with _temp_env({"FUNC_X": 100}):
                result = func()
            self.assertEqual(142, result)

        with self.subTest("set x and y from env"):
            with _temp_env({"FUNC_X": 100, "FUNC_Y": -1}):
                result = func()
            self.assertEqual(142, result)
