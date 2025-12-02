import os
import json
import hashlib
import difflib
from datetime import datetime
from pathlib import Path
import inspect


class SnapshotCache:
    def __init__(
        self,
        snapshot_root
    ):
        self.snapshot_root = Path(snapshot_root).expanduser()

    def run(self, func, args, kwargs):
        result = func(*args, **kwargs)

        if result is None:
            return

        fname = func.__name__
        timestamp = int(datetime.now().timestamp())

        args_repr = json.dumps(
            {
                "args": args,
                "kwargs": kwargs,
                "fname": fname,
            },
            sort_keys=True,
            default=str,
        )
        hash_id = hashlib.md5(args_repr.encode()).hexdigest()

        return {
            "args": args,
            "kwargs": kwargs,
            "fname": fname,
            "result": result,
            "timestamp": timestamp,
            "hash_id": hash_id,
        }

