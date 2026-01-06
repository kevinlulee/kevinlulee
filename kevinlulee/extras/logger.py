from __future__ import annotations

import sys
import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Literal, Union
from enum import IntEnum
from contextlib import contextmanager
from functools import wraps


LevelName = Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
OutputMode = Literal["console", "file", "both"]


class LogLevel(IntEnum):
    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    @classmethod
    def from_string(cls, level: LevelName) -> "LogLevel":
        return cls[level.upper()]


class LogFormatter:
    DEFAULT_FORMAT = "[{timestamp}] [{level}] [{name}] {message}"
    DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, fmt: str = None, datefmt: str = None):
        self.fmt = fmt or self.DEFAULT_FORMAT
        self.datefmt = datefmt or self.DEFAULT_DATE_FORMAT

    def format(self, record: dict) -> str:
        timestamp = record["timestamp"].strftime(self.datefmt)
        msg = self.fmt.format(
            timestamp=timestamp,
            level=record["level_name"],
            name=record["name"],
            message=record["message"],
            **record.get("extra", {})
        )
        if record.get("exception"):
            msg += "\n" + record["exception"]
        return msg


class JsonFormatter:
    def __init__(self, include_extra: bool = True):
        self.include_extra = include_extra

    def format(self, record: dict) -> str:
        output = {
            "timestamp": record["timestamp"].isoformat(),
            "level": record["level_name"],
            "logger": record["name"],
            "message": record["message"],
        }
        if record.get("exception"):
            output["exception"] = record["exception"]
        if self.include_extra and record.get("extra"):
            output["extra"] = record["extra"]
        return json.dumps(output, default=str)


class Handler:
    def __init__(self, formatter=None, level: LevelName = "TRACE"):
        self.formatter = formatter or LogFormatter()
        self.level = LogLevel.from_string(level)

    def set_level(self, level: LevelName) -> "Handler":
        self.level = LogLevel.from_string(level)
        return self

    def should_handle(self, level: LogLevel) -> bool:
        return level >= self.level

    def emit(self, record: dict):
        raise NotImplementedError

    def close(self):
        pass


class StreamHandler(Handler):
    def __init__(self, stream=None, **kwargs):
        super().__init__(**kwargs)
        self.stream = stream

    def emit(self, record: dict):
        msg = self.formatter.format(record)
        print(msg)


class FileHandler(Handler):
    def __init__(self, filename: Union[str, Path], mode: str = "a",
                 encoding: str = "utf-8", **kwargs):
        kwargs.setdefault("formatter", JsonFormatter())
        super().__init__(**kwargs)
        self.filename = Path(filename)
        self.mode = mode
        self.encoding = encoding
        self._file = None
        self._open()

    def _open(self):
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        self._file = open(self.filename, self.mode, encoding=self.encoding)

    def emit(self, record: dict):
        msg = self.formatter.format(record)
        # kx.appendfile(self.filename, msg)
        if self._file:
            msg = self.formatter.format(record)
            self._file.write(msg + "\n")
            self._file.flush()

    def close(self):
        if self._file:
            self._file.close()
            self._file = None


class RotatingFileHandler(FileHandler):
    def __init__(self, filename: Union[str, Path], max_bytes: int = 10_000_000,
                 backup_count: int = 5, **kwargs):
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self._filename = Path(filename)
        self._rotate_if_needed()
        super().__init__(filename, **kwargs)

    def _rotate_if_needed(self):
        if not self._filename.exists():
            return
        if self._filename.stat().st_size < self.max_bytes:
            return
        for i in range(self.backup_count - 1, 0, -1):
            src = self._filename.with_suffix(f".{i}")
            dst = self._filename.with_suffix(f".{i + 1}")
            if src.exists():
                src.rename(dst)
        self._filename.rename(self._filename.with_suffix(".1"))


class Logger:
    _instances: dict[str, "Logger"] = {}

    def __new__(cls, name: str = "root", **kwargs):
        if name not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[name] = instance
        return cls._instances[name]

    def __init__(self, name: str = "root", level: LevelName = "INFO",
                 filename: Union[str, Path] = None, max_bytes: int = None,
                 backup_count: int = 5):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self.name = name
        self.level = LogLevel.from_string(level)
        self._context: dict[str, Any] = {}
        self._mode: OutputMode = "console"
        self._stream_handler = StreamHandler()
        self._file_handler = None
        if filename:
            if max_bytes:
                self._file_handler = RotatingFileHandler(filename, max_bytes=max_bytes,
                                                         backup_count=backup_count)
            else:
                self._file_handler = FileHandler(filename)

    def set_level(self, level: LevelName) -> "Logger":
        self.level = LogLevel.from_string(level)
        return self

    def set_file(self, filename: Union[str, Path], max_bytes: int = None,
                 backup_count: int = 5) -> "Logger":
        filename = os.path.expanduser(filename)
        if self._file_handler:
            self._file_handler.close()
        if max_bytes:
            self._file_handler = RotatingFileHandler(filename, max_bytes=max_bytes,
                                                     backup_count=backup_count)
        else:
            self._file_handler = FileHandler(filename)
        return self

    def enable(self, mode: OutputMode) -> "Logger":
        if mode in ("file", "both") and not self._file_handler:
            raise ValueError("No file configured. Call set_file() first.")
        self._mode = mode
        return self

    def bind(self, **kwargs) -> "Logger":
        new_logger = object.__new__(Logger)
        new_logger._initialized = True
        new_logger.name = self.name
        new_logger.level = self.level
        new_logger._context = {**self._context, **kwargs}
        new_logger._mode = self._mode
        new_logger._stream_handler = self._stream_handler
        new_logger._file_handler = self._file_handler
        return new_logger

    def _make_record(self, level: LogLevel, message: str, exception: str = None, **extra) -> dict:
        return {
            "timestamp": datetime.now(timezone.utc),
            "level": level,
            "level_name": LogLevel(level).name,
            "name": self.name,
            "message": message,
            "exception": exception,
            "extra": {**self._context, **extra},
        }

    def _log(self, level: LogLevel, message: str, *args, exc_info: bool = False, **kwargs):
        if level < self.level:
            return
        if args:
            message = message.format(*args)
        exception = None
        if exc_info:
            exception = traceback.format_exc()
        record = self._make_record(level, message, exception, **kwargs)
        if self._mode in ("console", "both"):
            if self._stream_handler.should_handle(level):
                self._stream_handler.emit(record)
        if self._mode in ("file", "both"):
            if self._file_handler and self._file_handler.should_handle(level):
                self._file_handler.emit(record)

    def trace(self, message: str, *args, **kwargs):
        self._log(LogLevel.TRACE, message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs):
        self._log(LogLevel.DEBUG, message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        self._log(LogLevel.INFO, message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self._log(LogLevel.WARNING, message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        self._log(LogLevel.ERROR, message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        self._log(LogLevel.CRITICAL, message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        self._log(LogLevel.ERROR, message, *args, exc_info=True, **kwargs)

    @contextmanager
    def context(self, **kwargs):
        yield self.bind(**kwargs)

    def timed(self, func: Callable = None, *, level: LevelName = "INFO"):
        log_level = LogLevel.from_string(level)
        def decorator(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                start = datetime.now()
                result = fn(*args, **kwargs)
                elapsed = (datetime.now() - start).total_seconds()
                self._log(log_level, f"{fn.__name__} took {elapsed:.4f}s")
                return result
            return wrapper
        return decorator(func) if func else decorator

    def close(self):
        if self._file_handler:
            self._file_handler.close()

    @classmethod
    def get_logger(cls, name: str = "root") -> "Logger":
        return cls(name)


logger = Logger("app").get_logger('boo')
# logger.set_file("~/scratch/app.log")
# logger.enable("file")
# logger.info("goes to file only")
# logger.close()
# logger.enable("console")
# logger.info("goes to console only")

__all__ = [
    "Logger"
]
