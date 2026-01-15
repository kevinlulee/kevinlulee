from __future__ import annotations
import kevinlulee as kx


class CodeModule:
    def __init__(self, path):
        self.path = path
        self.module = kx.get_module(
            path, reload=True
        ) or kx.import_module_from_path(path)

    @property
    def symbols(self):
        return getattr(self.module, "__all__", None)

    def get_identifiers(self):
        return kx.collect(self.path, "^(?:def|class) ([a-zA-Z]\w+)")

    @property
    def name(self):
        return self.module.__name__

    def get(self, key):
        return getattr(self.module, key)

    def get_import_string(self):
        try:
            symbols = self.symbols or ["*"]
            return f"from {self.name} import {', '.join(symbols)}"
        except Exception as e:
            return f"{e}"

    def __repr__(self):
        return repr(self.module)


__all__ = ["CodeModule"]
