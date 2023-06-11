def bisect_function(func, lo, hi, target, *,
                    step=1, delta=0, invert=False, key=None):
    lo_val, hi_val = None, None
    best_val, best_res, best_pos = None, None, None
    if key is None:
        key = lambda x: x

    while lo <= hi:
        if lo_val is not None and hi_val is not None:
            assert (lo_val > hi_val) == invert
            pos = lo + (hi - lo) * (target - lo_val) / (hi_val - lo_val)
        else:
            pos = (lo + hi) / 2

        pos = round(pos / step) * step
    
        res = func(pos)
        val = key(res)
        # print(f'try {lo=} {hi=} {target=} {pos=} {val=}')
    
        if (val < target) != invert:
            lo = pos + step
            lo_val = val
        else:
            hi = pos - step
            hi_val = val

        if best_val is None or abs(target - val) < abs(target - best_val):
            best_val = val
            best_res = res
            best_pos = pos

        if abs(target - val) <= target * delta:
            break

    return best_res, best_pos
