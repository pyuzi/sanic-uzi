import typing as t

from collections.abc import Callable

from sanic import Sanic
from sanic.exceptions import SanicException
from sanic_ext.extensions.base import Extension
from sanic_ext.bootstrap import Config, Extend as BaseExtend, TEMPLATING_ENABLED

from sanic_ext.extensions.http.extension import HTTPExtension
from sanic_ext.extensions.openapi.extension import OpenAPIExtension
from sanic_ext.extensions.templating.extension import TemplatingExtension
from sanic_ext.utils.string import camel_to_snake

from uzi.containers import Container
from uzi.scopes import Scope

from .extension import UziExtension

# try:
#     from jinja2 import Environment
#     TEMPLATING_ENABLED = True
# except (ImportError, ModuleNotFoundError):
#     TEMPLATING_ENABLED = False


class Extend(BaseExtend):

    uzi_container: Container

    def __init__(
        self,
        app: Sanic,
        *,
        extensions: t.Optional[list[type[Extension]]] = None,
        config: t.Union[Config, dict[str, t.Any], None] = None,
        built_in_extensions: bool = True,
        **kwargs
    ) -> None:

        extensions = [
            *(extensions or ()), 
            UziExtension
        ]
        
        built_in_extensions and extensions.extend((
            OpenAPIExtension,
            HTTPExtension,
            *(TEMPLATING_ENABLED and (TemplatingExtension,) or ())
        ))

        self._uzi_scope = None

        super().__init__(
            app,
            extensions=extensions,
            built_in_extensions=False,
            config=config,
            **kwargs
        )


    @property
    def uzi_container(self) -> Container:
        return self._uzi_scope.container

    def add_dependency(
        self,
        type: type,
        constructor: Callable[..., t.Any] = None,
    ) -> None:
        if not self._uzi_scope:
            raise SanicException("Uzi extension not enabled")
        self.uzi_container.factory(type, constructor)

    def dependency(self, obj: t.Any, name: str = None, type: type = None) -> None:
        type = type or obj.__type__
        name = name or camel_to_snake(type.__name__)
        setattr(self.app.ctx._dependencies, name, obj)
        self.uzi_container.value(type, obj)