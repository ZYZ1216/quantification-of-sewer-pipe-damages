from typing import Type, Dict, Callable, TypeVar
from quantifiers.base import DamageQuantifier

T = TypeVar('T', bound=DamageQuantifier)

class QuantifierFactory:
    _registry: Dict[str, Type[DamageQuantifier]] = {}

    @classmethod
    def register(cls, label: str) -> Callable[[Type[T]], Type[T]]:
        def decorator(qclass: Type[T]) -> Type[T]:
            cls._registry[label] = qclass
            return qclass
        return decorator

    @classmethod
    def create(cls, label: str) -> DamageQuantifier:
        if label not in cls._registry:
            raise ValueError(f"No quantifier for {label}")
        return cls._registry[label]()
