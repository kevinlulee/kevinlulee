from __future__ import annotations

import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Union
from enum import IntEnum
from threading import RLock

LevelName = Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
OutputMode = Literal["console", "file", "both"]


class LogLevel(IntEnum):
    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    ALERT = 100

    @classmethod
    def from_string(cls, level: LevelName) -> "LogLevel":
        return cls[level.upper()]

    @classmethod
    def to_string(cls, level: LevelName) -> "LogLevel":
        return level.name

class LogFormatter:
    def format(self, record: dict) -> str:
        ts = record["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{ts}] [{record['level_name']}] [{record['name']}] {record['message']}"
        if record.get("exception"):
            msg += "\n" + record["exception"]
        return msg


class JsonFormatter:
    def format(self, record: dict) -> str:
        return json.dumps(
            {
                "timestamp": record["timestamp"].isoformat(),
                "level": record["level_name"],
                "logger": record["name"],
                "message": record["message"],
                "exception": record.get("exception"),
                "extra": record.get("extra"),
            },
            default=str,
        )


class Handler:
    def __init__(self, formatter=None, level: LevelName = "TRACE"):
        self.formatter = formatter or LogFormatter()
        self.level = LogLevel.from_string(level)

    def should_handle(self, level: LogLevel) -> bool:
        return level >= self.level

    def emit(self, record: dict):
        raise NotImplementedError

    def close(self):
        pass


class StreamHandler(Handler):
    def emit(self, record: dict):
        print(self.formatter.format(record))


class FileHandler(Handler):
    def __init__(self, filename: Path, **kwargs):
        kwargs.setdefault("formatter", JsonFormatter())
        super().__init__(**kwargs)
        self.filename = filename
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        self._file = open(self.filename, "a", encoding="utf-8")

    def emit(self, record: dict):
        self._file.write(self.formatter.format(record) + "\n")
        self._file.flush()

    def close(self):
        self._file.close()


class _LoggingCore:
    """
    Private singleton.
    Owns all handlers and global output mode.
    """

    def __init__(self):
        self._lock = RLock()
        self._stream_handler = StreamHandler()
        self._file_handlers: dict[Path, FileHandler] = {}
        self._mode: OutputMode = "console"  # default: log to file

    def set_mode(self, mode: OutputMode):
        self._mode = mode

    def resolve_path(self, raw: Union[str, Path]) -> Path:
        path = Path(os.path.expandvars(os.path.expanduser(str(raw))))
        return path.resolve()

    def get_file_handler(self, path: Path) -> FileHandler:
        with self._lock:
            if path not in self._file_handlers:
                self._file_handlers[path] = FileHandler(path)
            return self._file_handlers[path]

    def emit(self, record: dict, file_path: Path):
        mode =self._mode
        if mode in ("console", "both"):
            self._stream_handler.emit(record)

        if mode in ("file", "both"):
            handler = self.get_file_handler(file_path)
            handler.emit(record)

    def open_file_paths(self) -> list[Path]:
        return list(self._file_handlers.keys())

    def close(self):
        for handler in self._file_handlers.values():
            handler.close()
        self._file_handlers.clear()


_CORE = _LoggingCore()


class Logger:
    _loggers: dict[str, "Logger"] = {}

    def __init__(self, name: str, *, path: Union[str, Path]):
        self.name = name
        self.level = LogLevel.INFO
        self._context: dict[str, Any] = {}
        self._file_path = _CORE.resolve_path(path)

    # -------- factory --------

    @classmethod
    def get_logger(cls, name: str, *, path: Union[str, Path]) -> "Logger":
        if name in cls._loggers:
            return cls._loggers[name]

        logger = cls(name, path=path)
        cls._loggers[name] = logger
        return logger

    # -------- configuration --------

    def get_level(self):
        return LogLevel.to_string(self.level)
    def set_level(self, level: LevelName) -> "Logger":
        self.level = LogLevel.from_string(level)
        return self

    def set_output_mode(self, mode: OutputMode):
        _CORE.set_mode(mode)

    # -------- logging --------


    def strlog(self, level: str, message: str, caller: str, *args, exc_info=False, **extra):
        level = LogLevel.from_string(level)
        if level < self.level:
            return

        if args:
            message = message.format(*args)

        msg = f"[{level.name}] <{caller}> {message}"
        return msg

    def _log(self, level: LogLevel, message: str, *args, exc_info=False, **extra):
        if level < self.level:
            return

        if args:
            message = message.format(*args)

        exception = traceback.format_exc() if exc_info else None

        record = {
            "timestamp": datetime.now(timezone.utc),
            "level": level,
            "level_name": level.name,
            "name": self.name,
            "message": message,
            "exception": exception,
            "extra": extra,
        }

        _CORE.emit(record, self._file_path)

    def trace(self, msg, *a, **k): self._log(LogLevel.TRACE, msg, *a, **k)
    def debug(self, msg, *a, **k): self._log(LogLevel.DEBUG, msg, *a, **k)
    def info(self, msg, *a, **k): self._log(LogLevel.INFO, msg, *a, **k)
    def warn(self, msg, *a, **k): self._log(LogLevel.WARNING, msg, *a, **k)
    def error(self, msg, *a, **k): self._log(LogLevel.ERROR, msg, *a, **k)
    def critical(self, msg, *a, **k): self._log(LogLevel.CRITICAL, msg, *a, **k)

    def exception(self, msg, *a, **k):
        self._log(LogLevel.ERROR, msg, *a, exc_info=True, **k)

    # -------- diagnostics --------

    @classmethod
    def open_log_files(cls) -> list[Path]:
        return _CORE.open_file_paths()

    # -------- lifecycle --------

    @classmethod
    def shutdown(cls):
        _CORE.close()



if __name__ == '__main__':
    lo = Logger(name = 'asdf', path = 'asdf')
    print(LogLevel.to_string(lo.level))
