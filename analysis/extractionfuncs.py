import numpy as np

from .constants import ResultType
from .data import EdoData

grouper = lambda n, iterable: zip(*[iter(iterable)] * n)


def find_touch_indices():
    edo_data = EdoData()
    N_cutoff_at_end = int(6.0 * 50)  # assumed 6 seconds timeout with 50 Hz = 300 points
    N_touches = edo_data.fetch_markers("R2P", "touches", result_type=ResultType.INDEX)
    N_starts = edo_data.fetch_markers("R2P", "start", result_type=ResultType.INDEX)
    ratio = eval(edo_data.log["R2P"].get("ratio"))
    group_length = int(len(N_starts) / len(ratio))
    groups = list(grouper(group_length, N_starts))

    touch_indices = []
    for group in groups:
        _group = group + (group[-1] + N_cutoff_at_end,)
        for i in range(group_length):
            start, stop = _group[i], _group[i + 1]
            for touch in N_touches:
                if start <= touch <= stop:
                    break
                else:
                    touch = np.NaN
            touch_indices.append((start, touch, stop))
    return touch_indices


def find_calibration_indices():
    edo_data = EdoData()
    starts = edo_data.fetch_markers("CALIBRATION", "start", result_type=ResultType.INDEX)
    stops = edo_data.fetch_markers("CALIBRATION", "stop", result_type=ResultType.INDEX)
    return list(iter(zip(starts, stops)))
