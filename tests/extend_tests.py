
import pytest

from sanic import Sanic

from sanic_uzi import inject
from sanic_uzi.ext import Extend
from sanic_uzi.ext.extension import UziExtension



xfail = pytest.mark.xfail
parametrize = pytest.mark.parametrize


def basic_test():
    app = Sanic('test')
    Extend(app)
    