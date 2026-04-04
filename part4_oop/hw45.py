from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from part4_oop.interfaces import Cache, HasCache, Policy, Storage

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class DictStorage(Storage[K, V]):
    _data: dict[K, V] = field(default_factory=dict, init=False)

    def set(self, key: K, value: V) -> None:
        self._data[key] = value

    def get(self, key: K) -> V | None:
        return self._data.get(key, None)

    def exists(self, key: K) -> bool:
        return key in self._data

    def remove(self, key: K) -> None:
        self._data.pop(key, None)

    def clear(self) -> None:
        self._data.clear()


@dataclass
class FIFOPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        if key not in self._order:
            self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if len(self._order) > self.capacity:
            return self._order[0]
        return None

    def remove_key(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._order) != 0


@dataclass
class LRUPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)
        self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if len(self._order) > self.capacity:
            return self._order[0]
        return None

    def remove_key(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._order) != 0


@dataclass
class LFUPolicy(Policy[K]):
    capacity: int = 5
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)
    _last_added_key: K | None = None

    def register_access(self, key: K) -> None:
        self._key_counter[key] = self._key_counter.get(key, 0) + 1
        self._last_added_key = key

    def get_key_to_evict(self) -> K | None:
        if len(self._key_counter) > self.capacity:
            keys_except_last_added = [x for x in self._key_counter if x != self._last_added_key]

            if len(keys_except_last_added) != 0:
                return min(keys_except_last_added, key=lambda x: self._key_counter[x])
            return self._last_added_key

        return None

    def remove_key(self, key: K) -> None:
        self._key_counter.pop(key, None)

    def clear(self) -> None:
        self._key_counter.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._key_counter) != 0


class MIPTCache(Cache[K, V]):
    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.policy = policy
        self.storage = storage

    def set(self, key: K, value: V) -> None:
        self.policy.register_access(key)
        self.storage.set(key, value)

        key_to_evict = self.policy.get_key_to_evict()
        if key_to_evict is not None:
            self.policy.remove_key(key_to_evict)
            self.storage.remove(key_to_evict)

    def get(self, key: K) -> V | None:
        if key in self.storage:
            self.policy.register_access(key)
        return self.storage.get(key)

    def exists(self, key: K) -> bool:
        return self.storage.exists(key)

    def remove(self, key: K) -> None:
        if key in self.storage:
            self.policy.remove_key(key)
            self.storage.remove(key)

    def clear(self) -> None:
        self.policy.clear()
        self.storage.clear()


class CachedProperty[V]:
    def __init__(self, func: Callable[..., V]) -> None:
        self.func = func

    def __get__(self, instance: HasCache[Any, Any] | None, owner: type) -> Any:
        if instance is None:
            return self

        func_name = self.func.__name__

        if instance.cache.exists(func_name):
            return instance.cache.get(func_name)

        value = self.func(instance)
        instance.cache.set(func_name, value)
        return value
