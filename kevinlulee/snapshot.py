

import os
import json
import hashlib
import difflib
from datetime import datetime
from pathlib import Path
import inspect
class SnapshotCache:
    def __init__(self, dry_run=False, overwrite=False, snapshot_root="/home/kdog3682/.kdog3682/snapshots", description='', tag = ''):
        self.dry_run = dry_run
        self.overwrite = overwrite
        self.snapshot_root = Path(snapshot_root)
        self.description = description
        self.tag = tag

    def run(self, func, *args, **kwargs):
        result = func(*args, **kwargs)

        if not result:
            print('no result')
            return

        func_name = func.__name__
        source_file = inspect.getsourcefile(func)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        args_repr = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
        args_hash = hashlib.md5(args_repr.encode()).hexdigest()

        snapshot_dir = self.snapshot_root / func_name
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        snapshot_file = snapshot_dir / f"{args_hash}.json"

        snapshot_data = {
            'timestamp': timestamp,
            'file': source_file,
            'args': args_repr,
            'result': result,
            'tag': self.tag,
            'func': func_name,
            'description': self.description
        }

        if snapshot_file.exists() and not self.overwrite:
            with open(snapshot_file, 'r') as f:
                previous_snapshot = json.load(f)

            prev_result_str = json.dumps(previous_snapshot['result'], indent=2, sort_keys=True, default=str)
            curr_result_str = json.dumps(result, indent=2, sort_keys=True, default=str)

            if prev_result_str != curr_result_str:
                print("--- Snapshot Diff ---")
                diff = difflib.unified_diff(
                    prev_result_str.splitlines(),
                    curr_result_str.splitlines(),
                    fromfile='previous',
                    tofile='current',
                    lineterm=''
                )
                print("\n".join(diff))
            else:
                print(result)
                print('snapshots match!')
        else:
            if not self.dry_run:
                with open(snapshot_file, 'w') as f:
                    json.dump(snapshot_data, f, indent=2, default=str)
                print(f"[snapshot saved] {snapshot_file}")
            else:
                import ascii

                if len(args) == 1 and not kwargs:
                    ascii.side_by_side(args[0], result, headers=('input', 'output'))
                else:
                    print(json.dumps(snapshot_data, indent=2))
                    print(f"[dry run] Would save snapshot: {snapshot_file}")

        return result

    def check(self, tag, func, *args, **kwargs):
        func_name = func.__name__
        snapshot_dir = self.snapshot_root / func_name

        for file in snapshot_dir.glob("*.json"):
            with open(file, 'r') as f:
                snapshot = json.load(f)
                if snapshot.get('tag') == tag:
                    ref_result_str = json.dumps(snapshot['result'], indent=2, sort_keys=True, default=str)
                    curr_result = func(*args, **kwargs)
                    curr_result_str = json.dumps(curr_result, indent=2, sort_keys=True, default=str)

                    if ref_result_str != curr_result_str:
                        print("--- Check Diff ---")
                        diff = difflib.unified_diff(
                            ref_result_str.splitlines(),
                            curr_result_str.splitlines(),
                            fromfile='reference',
                            tofile='current',
                            lineterm=''
                        )
                        print("\n".join(diff))
                    else:
                        print(curr_result)
                        print("check passed: results match reference snapshot")
                    return

        print(f"no reference snapshot found with description: {tag}")

    def clear(self, func):
        func_name = func.__name__
        snapshot_dir = self.snapshot_root / func_name

        if snapshot_dir.exists():
            for file in snapshot_dir.glob("*.json"):
                file.unlink()
            print(f"[cleared] all snapshots for '{func_name}'")
        else:
            print(f"[not found] no snapshots for '{func_name}'")

