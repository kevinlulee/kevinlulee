import sympy as sp
from itertools import product
from typing import Literal
import kevinlulee as kx

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

def _iterative_range(radius, domain, positive):
    if domain == 'N':
        lo = 0 if not positive else 1
        return range(lo, radius + 1)
    if positive:
        return range(1, radius + 1)
    return range(-radius, radius + 1)

def _search_int(expr, tgt, vars_sorted, domain, positive, distinct, max_solutions, max_radius):
    sols = []
    seen = set()
    radius = 0
    while True:
        rng = _iterative_range(radius, domain, positive)
        for values in product(rng, repeat=len(vars_sorted)):
            if values in seen:
                continue
            seen.add(values)
            assignment = {v: val for v, val in zip(vars_sorted, values)}
            if not _passes_constraints(assignment, distinct, positive, domain, vars_sorted):
                continue
            if sp.simplify(expr.subs(assignment) - tgt) == 0:
                sols.append(assignment)
                if len(sols) >= max_solutions:
                    return sols, radius
        if radius >= max_radius:
            return sols, radius
        nxt = 1 if radius == 0 else radius * 2
        if nxt > max_radius:
            nxt = max_radius
        radius = nxt

def _smart_max_radius(expr, tgt, nvars):
    zeros = {s: 0 for s in expr.free_symbols}
    expr0 = sp.simplify(expr.subs(zeros))
    bad = (expr0.has(sp.zoo) or expr0.has(sp.oo) or expr0.has(sp.nan) or not expr0.is_number)
    base_scale = abs(sp.simplify(tgt - expr0)) if not bad else abs(sp.simplify(tgt))
    if base_scale.is_integer():
        try_scale = int(sp.Integer(base_scale))
    else:
        try_scale = int(abs(float(base_scale)))
    est = max(try_scale * 2, 32)
    est += 4 * max(0, nvars - 3)
    return min(est, 2048)

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
    return {str(k): v for k, v in d.items()}

def _name_solutions(sol_list):
    return [_name_dict(d) for d in sol_list]

# ---- main API ----

def solve_template(
    template: str,
    target,
    *,
    domain: Literal['Z','N','R','Q'] = 'Z',
    variables=None,
    method: Literal['auto','search','symbolic'] = 'auto',
    positive: bool | None = None,
    distinct: bool = False,
    max_solutions: int = 100,
    params: dict | None = None
):
    """
    Solve a template like "a + b*c" against a target.
    Domains: 'Z' integers, 'N' nonnegative, 'R' reals, 'Q' rationals (filtered).
    """
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
            if positive is True:
                sols = [d for d in sols if d[v] > 0]
            return {'pivot': str(v), 'solutions': _name_solutions(sols), 'free': ()}
        # ConditionSet or Interval/etc.: return symbolic description
        return {'pivot': str(v), 'solutions': [{'solution_set': solset}], 'free': ()}

    # --- Multi-variable: choose method ---
    if method == 'auto':
        method_use = 'search' if domain in ('Z','N') else 'symbolic'
    else:
        method_use = method

    if method_use == 'search':
        max_radius = _smart_max_radius(expr, tgt, len(vars_sorted))
        sols, used_radius = _search_int(expr, tgt, vars_sorted, domain, positive, distinct, max_solutions, max_radius)
        return sols
        return {
            'solutions': _name_solutions(sols),
            'meta': {
                'variables': [v.name for v in vars_sorted],
                'domain': domain,
                'positive': positive,
                'distinct': distinct,
                'solutions_found': len(sols),
                'searched_radius': used_radius,
                'max_radius': max_radius
            }
        }

    # --- Multi-variable symbolic: pivot on first
    main = vars_sorted[0]
    others = tuple(vars_sorted[1:])
    sol = sp.solve(eq, main, dict=True)
    if sol:
        return _name_solutions(sol)
        return {'pivot': str(main), 'solutions': _name_solutions(sol), 'free': tuple(s.name for s in others)}

    # Try other pivots if the first fails
    candidates = []
    for pivot in vars_sorted:
        s = sp.solve(eq, pivot, dict=True)
        if s:
            candidates.append({'pivot': str(pivot), 'solutions': _name_solutions(s), 'free': tuple(sym.name for sym in vars_sorted if sym != pivot)})
    return candidates
    return {'multi_pivot': True, 'candidates': candidates}

# ---- tiny demos (call one at a time with kx.pretty_print) ----

def demo(which: str):  
    if which == 'one_Z':
        res = solve_template("a + 12", 36, domain='Z')
        print(res); return
    if which == 'one_R':
        res = solve_template("a + 12", 10000, domain='R')
        print(res); return
    if which == 'one_N':
        res = solve_template("a - 5", 88, domain='N', positive=True)
        print(res); return
    if which == 'multi_symbolic':
        res = solve_template("a + b*c", 12, domain='R')
        print(res); return
    if which == 'multi_search':
        res = solve_template("a*b*c", 12, domain='Z', positive=True, max_solutions=20)
        print(res); return

demo('multi_search') # [ 'one_Z', 'one_R', 'one_N', 'multi_symbolic', 'multi_search' ]

