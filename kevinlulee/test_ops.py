from kevinlulee.ao import to_array


PREFERRED_TEST_CASE_KEYS = ("input", "template", "x", "in", "entry", "args")
RESERVED_TEST_CASE_KEYS = {
    "expect",
    "kwargs",
    "index",
    "result",
    "ok",
    "passed",
    "failed",
    "total",
    "results",
}


def sniff_dictionary_key(first, preferred_keys=[], reserved_keys=[]):
    # Prefer conventional names if present
    for preferred in preferred_keys:
        if preferred in first and preferred not in reserved_keys:
            return preferred

    candidates = [k for k in first if k not in reserved]
    if not candidates:
        raise ValueError("No input key found in the first case.")
    return candidates[0]  # preserve dict insertion order


def run_test_cases(cases, fn, input_key=None):
    if not input_key:
        input_key = sniff_dictionary_key(
            cases[0], PREFERRED_TEST_CASE_KEYS, RESERVED_TEST_CASE_KEYS
        )
    results = []
    for idx, case in enumerate(cases, 1):
        args = to_array(case[input_key])
        expect = case["expect"]
        kwargs = case.get("kwargs", {})
        result = None
        error = None
        try:
            result = fn(*args, **kwargs)
        except Exception as e:
            error = e
        p = {
            "index": idx,
            "args": args,
            "kwargs": kwargs,
            "expect": expect,
            'result': result,
            "ok": result == expect,
        }
        if error:
            p["error"] = str(error)
        results.append(p)

    summary = {
        "results": results,
        "total": len(results),
        "passed": sum(1 for r in results if r["ok"]),
        "failed": sum(1 for r in results if not r["ok"]),
    }
    return summary
