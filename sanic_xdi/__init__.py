from types import MethodType
import typing as t 
from collections.abc import Callable
from functools import partial, update_wrapper

from xdi import providers


from sanic import Request, Sanic
from sanic.router import Router







def inject(handler: Callable, /, *args, **kwds):
    if isinstance(handler, partial):
        func = handler.func
    else:
        func = handler      

    if hasattr(func, '__xdi_provider__'):
        raise ValueError(f'{handler!s} already wired')

    elif isinstance(func, MethodType):
        func, *args = func.__func__, func.__self__, *args

    provider = providers.Partial(func, *args, **kwds)

    def wrapper(req: t.Union[Sanic, Request, Router], *a, **kw):
        nonlocal provider
        return req.ctx._xdi_injector(provider, req, *a, **kw)
    
    update_wrapper(wrapper, func)
    wrapper.__xdi_provider__ = provider

    return wrapper



