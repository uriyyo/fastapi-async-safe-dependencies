from .types import DependantCall, DependantCallPredicate

_EXT_PREDICATES: list[DependantCallPredicate] = []

try:  # pragma: no cover
    from dependency_injector.wiring import Provide

    def _dependency_injector_predicate(func: DependantCall) -> bool:
        return isinstance(func, Provide)

    _EXT_PREDICATES.append(_dependency_injector_predicate)
except ImportError:  # pragma: no cover
    Provide = None  # type: ignore


def extensions_predicate(func: DependantCall) -> bool:
    return any(predicate(func) for predicate in _EXT_PREDICATES)


__all__ = [
    "extensions_predicate",
]
