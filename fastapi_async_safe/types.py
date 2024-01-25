from typing import Any, Callable

from typing_extensions import TypeAlias

DependantCall: TypeAlias = Callable[..., Any]
DependantCallPredicate: TypeAlias = Callable[[DependantCall], bool]

__all__ = [
    "DependantCall",
    "DependantCallPredicate",
]
