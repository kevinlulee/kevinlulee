import os
import json
import hashlib
import difflib
from datetime import datetime
from pathlib import Path
import inspect

def dumper(value):
            return json.dumps(
                value,
                indent=2,
                sort_keys=True,
                default=str,
            )

class SnapshotCache:
    def __init__(
        self,
        snapshot_root="~/.kdog3682/snapshots",
    ):
        self.snapshot_root = Path(snapshot_root).expanduser()

    def run(self, func, *args, **kwargs):
        result = func(*args, **kwargs)

        if result is None:
            return

        key = 'asdf'
        description = 'asdf'

        fname = func.__name__
        src_file = inspect.getsourcefile(func)
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

        snapshot_dir = self.snapshot_root / key
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        snapshot_file = snapshot_dir / f"{hash_id}.json"

        snapshot_data = {
            "timestamp": timestamp,
            "file": src_file,
            "args": args_repr,
            "result": result,
            "func": fname,
            "description": description,
        }

        if snapshot_file.exists():
            prev_result = kx.readfile(snapshot_file)

            kx.ascii.side_by_side()

            if prev_result_str != curr_result_str:
                print("--- Snapshot Diff ---")
                diff = difflib.unified_diff(
                    prev_result_str.splitlines(),
                    curr_result_str.splitlines(),
                    fromfile="previous",
                    tofile="current",
                    lineterm="",
                )
                print("\n".join(diff))
            else:
                print(result)
                print("snapshots match!")
        else:
            kx.appendfile(snapshot_file, [snapshot_data], verbose = True)

        return result

    def check(self, tag, func, *args, **kwargs):
        fname = func.__name__
        snapshot_dir = self.snapshot_root / fname

        for file in snapshot_dir.glob("*.json"):
            with open(file, "r") as f:
                snapshot = json.load(f)
                if snapshot.get("tag") == tag:
                    ref_result_str = json.dumps(
                        snapshot["result"],
                        indent=2,
                        sort_keys=True,
                        default=str,
                    )
                    curr_result = func(*args, **kwargs)
                    curr_result_str = json.dumps(
                        curr_result, indent=2, sort_keys=True, default=str
                    )

                    if ref_result_str != curr_result_str:
                        print("--- Check Diff ---")
                        diff = difflib.unified_diff(
                            ref_result_str.splitlines(),
                            curr_result_str.splitlines(),
                            fromfile="reference",
                            tofile="current",
                            lineterm="",
                        )
                        print("\n".join(diff))
                    else:
                        print(curr_result)
                        print("check passed: results match reference snapshot")
                    return

        print(f"no reference snapshot found with description: {tag}")

    def clear(self, func):
        fname = func.__name__
        snapshot_dir = self.snapshot_root / fname

        if snapshot_dir.exists():
            for file in snapshot_dir.glob("*.json"):
                file.unlink()
            print(f"[cleared] all snapshots for '{fname}'")
        else:
            print(f"[not found] no snapshots for '{fname}'")


# ======================================
# simple case:
# ======================================
# templater(1,2,3)
#
# --------------------------------------
#
# resulthere
