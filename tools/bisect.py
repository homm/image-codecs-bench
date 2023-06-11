def bisect_function(func, lo, hi, target, *, step=1, delta=0, invert=False):
    lo_val, hi_val = None, None
    best_val, best_pos = None, None

    while lo <= hi:
        if lo_val is not None and hi_val is not None:
            pos = lo + (hi - lo) * (target - lo_val) / (hi_val - lo_val)
        else:
            pos = (lo + hi) / 2

        pos = round(pos / step) * step
    
        val = func(pos)
        print(f'try {lo=} {hi=} {target=} {pos=} {val=}')
    
        if (val < target) != invert:
            lo = pos + step
            lo_val = val
        else:
            hi = pos - step
            hi_val = val

        if best_val is None or abs(target - val) < abs(target - best_val):
            best_val = val
            best_pos = pos

        if abs(target - val) <= target * delta:
            break

    return best_val, best_pos
