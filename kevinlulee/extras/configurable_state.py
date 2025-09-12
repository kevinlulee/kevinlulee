from collections.abc import MutableMapping
from typing import Any, Iterator, Mapping


class ConfigurableState(MutableMapping[str, Any]):
    __slots__ = ("_data",)

    def __init__(self, data: Mapping[str, Any] | None = None, **kwargs: Any) -> None:
        object.__setattr__(self, "_data", {})
        if data is not None:
            self.update(data)
        if kwargs:
            self.update(kwargs)

    # ---------- helpers ----------
    def _wrap(self, value: Any) -> Any:
        if isinstance(value, dict):
            return type(self)(value)
        if isinstance(value, list):
            return [self._wrap(v) for v in value]
        return value

    def _unwrap(self, value: Any) -> Any:
        if isinstance(value, ConfigurableState):
            return value.to_dict()
        if isinstance(value, list):
            return [self._unwrap(v) for v in value]
        return value

    # ---------- attribute access (autovivifying) ----------
    def __getattr__(self, name: str) -> Any:
        data = object.__getattribute__(self, "_data")
        if name in data:
            return data[name]
        child = type(self)()
        data[name] = child
        return child

    def __setattr__(self, name: str, value: Any) -> None:
        if name in type(self).__dict__ or name in self.__slots__:
            object.__setattr__(self, name, value)
        else:
            self._data[name] = self._wrap(value)

    def __delattr__(self, name: str) -> None:
        if name in self._data:
            del self._data[name]
        else:
            object.__delattr__(self, name)

    # ---------- mapping protocol ----------
    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = self._wrap(value)

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    # ---------- convenience ----------
    def to_dict(self) -> dict[str, Any]:
        return {k: self._unwrap(v) for k, v in self._data.items()}

    def copy(self) -> "ConfigurableState":
        return type(self)(self.to_dict())

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.to_dict()!r})"


if __name__ == "__main__":
    state = ConfigurableState()
    state.style.header.align = "center"
    state.theme.colors.primary = "#3b82f6"
    state["threshold"] = 0.75
    print(state.to_dict())

