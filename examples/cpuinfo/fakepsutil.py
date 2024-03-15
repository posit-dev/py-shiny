"""Generates synthetic data"""

import numpy as np


def cpu_count(logical: bool = True):
    return 8 if logical else 4


rng = np.random.default_rng()
last_sample = rng.uniform(0, 100, size=cpu_count(True))


def cpu_percent(percpu: bool = False):
    global last_sample
    delta = rng.normal(scale=10, size=len(last_sample))
    last_sample = (last_sample + delta).clip(0, 100)
    if percpu:
        return last_sample.tolist()
    else:
        return last_sample.mean()
