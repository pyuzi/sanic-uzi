"""Application module."""

from asyncio import gather
from typing import Any
from sanic import Request, Sanic
from sanic_routing import Route

from sanic_ext.extensions.http.extension import HTTPExtension
from sanic_ext.extensions.openapi.extension import OpenAPIExtension

from . import handlers
from uzi import Scope
from uzi.injectors import Injector
from .di import ioc, inject
from .services import search, giphy



def create_app(use_di=False) -> Sanic:
    """Create and return Sanic application."""
    app: Sanic = Sanic("ioc", configure_logging=False)
    
    # app.config.AUTO_EXTEND = not use_di
    # app.config.ACCESS_LOG = True

    if use_di:
        app.extend(extensions=[
            OpenAPIExtension,
            HTTPExtension,
        ], built_in_extensions=False)

        app.add_route(inject(handlers.sindex), "/s")
        app.add_route(inject(handlers.aindex), "/a")
        scope = Scope(ioc)
        @app.on_request
        def setup_request_injector(request: Request):
            request.ctx._uzi_injector = Injector(scope)
            # print('***<on_request>***')

        # @app.on_response
        # async def teardown_request_injector(request: Request, res):
        #     await request.ctx.injector_context.exitstack.aclose()
        #     # print('***<on_response>***')
    else:
        app.ext.add_dependency(giphy.GiphyClient)
        app.ext.add_dependency(search.SearchService, search.SearchService.make)
        app.add_route(handlers.sindex, "/s")
        app.add_route(handlers.aindex, "/a")

    return app

