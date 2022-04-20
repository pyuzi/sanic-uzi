from functools import partial
from inspect import getmembers, isfunction
import typing as t
from sanic import Sanic
from sanic.constants import HTTP_METHODS
from sanic_ext import Config
from sanic_ext.extensions.base import Extension
from xdi.containers import Container

from xdi.scopes import Scope, NullScope

from .. import inject


if t.TYPE_CHECKING:
    from . import Extend


class XDIExtension(Extension):
    
    name = "xdi"

    config: 'Config'

    def __init__(self, app: Sanic, config: Config) -> None:
        super().__init__(app, config)
        self.auto_wire = config.get('XDI_AUTO_WIRE', True)
    
    def label(self):
        return f"{len(self.scope.container)} added"

    def _setup(self, ext: 'Extend'):
        ctx = self.app.ctx
        ctx_attrs = ('xdi_container', 'xdi_scope', 'xdi_base_scope')
        container, scope, base_scope = (getattr(ctx, n, None) for n in ctx_attrs)

        if container:
            if not scope:
                scope = Scope(container, base_scope)
            elif not container is scope.container:
                raise ValueError(f'scope container mis-match')
        elif scope:
            container = scope.container
        elif not container is False:
            container = Container(self.app.name)
            scope = Scope(container, base_scope)
        
        ext._xdi_scope = ctx.xdi_container, ctx.xdi_scope = container, scope

    def startup(self, bootstrap: 'Extend') -> None:
        self._setup(bootstrap)
        self.auto_wire and self._wire_entrypoints()

    def _wire_entrypoints(self):
        app = self.app

        @app.after_server_start
        async def wrap_entrypoints(app: Sanic, _):
            
            scope: Scope = app.ctx.xdi_scope
            container = scope.container

            for route in app.router.routes:
                if ".openapi." in route.name:
                    continue
                handlers = [(route.name, route.handler)]
                viewclass = getattr(route.handler, "view_class", None)
                if viewclass:
                    handlers = [
                        (f"{route.name}_{name}", member)
                        for name, member in getmembers(
                            viewclass, _http_method_predicate
                        )
                    ]
                for name, handler in handlers:
                    if hasattr(handler, "__auto_handler__"):
                        continue
                    if isinstance(handler, partial):
                        if handler.func == app._websocket_handler:
                            handler = handler.args[0]
                        else:
                            handler = handler.func
                    try:
                        hints = t.get_type_hints(handler)
                    except TypeError:
                        continue
                    
                    # inject()
                    
                    # injections: dict[
                    #     str, tuple[type, t.Optional[t.Callable[..., t.Any]]]
                    # ] = {
                    #     param: (
                    #         annotation,
                    #         injection_registry[annotation],
                    #     )
                    #     for param, annotation in hints.items()
                    #     if annotation in injection_registry
                    # }
                    # registry.register(name, injections)




def _http_method_predicate(member):
    return isfunction(member) and member.__name__ in HTTP_METHODS

