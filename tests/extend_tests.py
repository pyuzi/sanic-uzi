
import pytest

from sanic import Sanic

from sanic_xdi import inject
from sanic_xdi.ext import Extend
from sanic_xdi.ext.extension import XDIExtension



xfail = pytest.mark.xfail
parametrize = pytest.mark.parametrize


def basic_test():
    app = Sanic('test')
    Extend(app)
    