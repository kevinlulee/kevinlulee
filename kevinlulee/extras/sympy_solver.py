
import sympy as sp
from itertools import product
from typing import Literal, TypedDict
import kevinlulee as kx

class Solution(TypedDict):
    """A single solution mapping variable names to their values."""
    pass  # Dynamic keys, all float values

# ---- helpers ----

def _normalize_vars(expr, variables):
    if variables is None:
        return sorted(expr.free_symbols, key=lambda s: s.name)
    if isinstance(variables, str):
        return list(sp.symbols(variables, real=True))
    return list(sp.symbols(' '.join(map(str, variables)), real=True))

def _passes_constraints(assignment, distinct, positive, domain, vars_sorted):
    if distinct:
        vals = [assignment[v] for v in vars_sorted]
        if len(set(vals)) != len(vals):
            return False
    if positive is True:
        for v in vars_sorted:
            if assignment[v] <= 0:
                return False
    if domain == 'N':
        for v in vars_sorted:
            if assignment[v] < 0:
                return False
    return True

def _iterative_range(radius, domain, positive, disallow=None):
    if domain == 'N':
        lo = 0 if not positive else 1
        r = range(lo, radius + 1)
    elif positive:
        r = range(1, radius + 1)
    else:
        r = range(-radius, radius + 1)

    if disallow is None:
        return r

    if isinstance(disallow, (list, tuple, set)):
        return iter(x for x in r if x not in disallow)
    else:
        return iter(x for x in r if x != disallow)

def _deduplicate_solutions(sols, vars_sorted):
    """Remove solutions that are permutations of each other."""
    seen_multisets = set()
    unique_sols = []

    for sol in sols:
        # Create a sorted tuple of values (canonical form)
        values = tuple(sorted(sol[v] for v in vars_sorted))

        if values not in seen_multisets:
            seen_multisets.add(values)
            unique_sols.append(sol)

    return unique_sols

def _search_int(expr, tgt, vars_sorted, domain, positive, distinct, max_solutions, max_radius, deduplicate=True, disallow = None):
    sols = []
    seen = set()
    radius = 0
    while True:
        rng = _iterative_range(radius, domain, positive, disallow)
        for values in product(rng, repeat=len(vars_sorted)):
            if values in seen:
                continue
            seen.add(values)
            assignment = {v: val for v, val in zip(vars_sorted, values)}
            if not _passes_constraints(assignment, distinct, positive, domain, vars_sorted):
                continue
            if sp.simplify(expr.subs(assignment) - tgt) == 0:
                sols.append(assignment)
                if deduplicate and len(sols) >= max_solutions * 10:
                    # Early dedup if we've collected many solutions
                    sols = _deduplicate_solutions(sols, vars_sorted)
                    if len(sols) >= max_solutions:
                        return sols[:max_solutions], radius
                elif not deduplicate and len(sols) >= max_solutions:
                    return sols, radius
        if radius >= max_radius:
            if deduplicate:
                sols = _deduplicate_solutions(sols, vars_sorted)
            return sols[:max_solutions] if len(sols) > max_solutions else sols, radius
        nxt = 1 if radius == 0 else radius * 2
        if nxt > max_radius:
            nxt = max_radius
        radius = nxt

def _smart_max_radius(expr, tgt, nvars):
    if tgt.is_number:
        mag = int(abs(sp.Integer(tgt)))
        if mag == 0:
            base = 8
        elif mag <= 12:
            base = 12
        elif mag <= 100:
            base = 24
        else:
            base = 32
    else:
        base = 16
    return min(64, base + 4 * max(0, nvars - 3))

def _name_dict(d):
    return {str(k): kx.possibly_normalize_number(float(v)) for k, v in d.items()}

def _name_solutions(sol_list):
    return [_name_dict(d) for d in sol_list]

# ---- main API ----

from kevinlulee.extras.persistent_file_cache import PersistentFileCache

# @PersistentFileCache(verbose = False)
def sympy_solver(
    template: str,
    target = None,
    domain: Literal['Z','N','R','Q'] = 'N',
    variables=None,
    method: Literal['auto','search','symbolic'] = 'auto',
    only_positive_answers: bool = False,
    distinct_solutions: bool = False,
    max_solutions: int = 5,
    params: dict | None = None,
    deduplicate: bool = True  # NEW PARAMETER
):
    """
    Solve a template like "a + b*c" against a target.
    Domains: 'Z' integers, 'N' nonnegative, 'R' reals, 'Q' rationals (filtered).

    deduplicate: If True, remove solutions that are permutations of each other
                 (e.g., {a:1, b:2, c:3} and {a:3, b:1, c:2} are considered equivalent)
    """
    if target is None:
        if '=' in template:
            template, target = kx.split(template, '=')
        else:
            raise Exception("no target provided")

    is_pure_mult_div = not kx.test(template, '[+-]')
    is_pure_add_sub = not kx.test(template, '[*/]')
    expr = sp.sympify(template)
    tgt  = sp.sympify(target)

    if params:
        expr = expr.subs(params)
        tgt  = tgt.subs(params)

    vars_sorted = _normalize_vars(expr, variables)
    eq = sp.Eq(expr, tgt)

    # --- Single-variable fast path via solveset ---
    if len(vars_sorted) == 1:
        v = vars_sorted[0]
        if domain == 'Z':
            solset = sp.solveset(eq, v, domain=sp.S.Integers)
        elif domain == 'N':
            solset = sp.solveset(eq, v, domain=sp.S.Integers)
            solset = solset.intersect(sp.Interval.Ropen(0, sp.oo))
        elif domain == 'R':
            solset = sp.solveset(eq, v, domain=sp.S.Reals)
        else:  # 'Q'
            solset = sp.solveset(eq, v, domain=sp.S.Reals)
            solset = sp.FiniteSet(*[s for s in solset if getattr(s, "is_rational", False)])

        if isinstance(solset, sp.FiniteSet):
            sols = [{v: s} for s in solset]
            if only_positive_answers is True:
                sols = [d for d in sols if d[v] > 0]

            return _name_solutions(sols)
        else:
            return _name_solutions(solset)

    # --- Multi-variable: choose method ---
    if method == 'auto':
        method_use = 'search' if domain in ('Z','N') else 'symbolic'
    else:
        method_use = method

    if method_use == 'search':
        max_radius = _smart_max_radius(expr, tgt, len(vars_sorted))
        disallow = [1, -1] if is_pure_mult_div else None
        if disallow is None:
            disallow = [0, 1, -1] if is_pure_add_sub else None
        sols, used_radius = _search_int(expr, tgt, vars_sorted, domain, only_positive_answers, distinct_solutions, max_solutions, max_radius, deduplicate, disallow)
        return _name_solutions(sols)

    # --- Multi-variable symbolic: pivot on first
    main = vars_sorted[0]
    others = tuple(vars_sorted[1:])
    sol = sp.solve(eq, main, dict=True)
    if sol:
        return _name_solutions(sol)

    candidates = []
    for pivot in vars_sorted:
        s = sp.solve(eq, pivot, dict=True)
        if s:
            candidates.append(_name_solutions(s))

    return candidates

# ---- demo ----

def demo_comparison():
    res2 = sympy_solver("a - 5", 12)
    # res3 = sympy_solver("a * b * c", 12)
    kx.pretty_print(res2)
    # kx.pretty_print(res3)

if __name__ == "__main__":
    demo_comparison()

