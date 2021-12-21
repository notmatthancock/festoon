import unittest
from unittest import mock

from festoon.logging_tools import format_call, logit, timeit


def func1(x, y, z=3):
    pass


def func2(*args):
    pass


class TestDefaultFormatCall(unittest.TestCase):
    def test_func1_all_args(self):
        args = (1, 2, 3)
        kwargs = {}
        message = format_call(func1, args, kwargs)
        self.assertEqual("CALL func1(x=1, y=2, z=3)", message)

    def test_func1_all_kwargs(self):
        args = tuple()
        kwargs = {"x": 1, "y": 2, "z": 3}
        message = format_call(func1, args, kwargs)
        self.assertEqual("CALL func1(x=1, y=2, z=3)", message)

    def test_func1_mix_args_kwargs(self):
        args = (1, 2)
        kwargs = {"z": 3}
        message = format_call(func1, args, kwargs)
        self.assertEqual("CALL func1(x=1, y=2, z=3)", message)

    def test_func2(self):
        message = format_call(func2, (1, 2, 3), {})
        self.assertEqual("CALL func2(1, 2, 3)", message)


class TestLogit(unittest.TestCase):
    def test_fmtcall_called(self):
        fmtcall = mock.Mock()

        @logit(fmtcall=fmtcall)
        def func():
            pass

        func()
        fmtcall.assert_called_once()

    def test_fmtdone_called(self):
        fmtdone = mock.Mock()

        @logit(fmtdone=fmtdone)
        def func():
            pass

        func()
        fmtdone.assert_called_once()

    def test_fmtexcp_called(self):
        fmtexcp = mock.Mock()

        @logit(fmtexcp=fmtexcp)
        def func():
            raise Exception

        with self.assertRaises(Exception):
            func()
            fmtexcp.assert_called_once()


class TestTimeit(unittest.TestCase):
    def test_fmttime_called(self):
        fmttime = mock.Mock()

        @timeit(fmttime=fmttime)
        def func():
            pass

        func()
        fmttime.assert_called_once()
