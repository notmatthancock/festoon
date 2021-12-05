import unittest
from unittest import mock

from festoon.logging_tools import logit, timeit


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
