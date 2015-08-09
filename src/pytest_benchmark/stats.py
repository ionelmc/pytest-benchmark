from __future__ import division

import statistics


class Stats(object):
    fields = "min", "max", "mean", "stddev", "rounds", "median", "iqr"

    def __init__(self):
        self.data = []

    def update(self, duration):
        self.data.append(duration)

    @property
    def total(self):
        return sum(self.data)

    @property
    def min(self):
        return min(self.data)

    @property
    def max(self):
        return max(self.data)

    @property
    def mean(self):
        return statistics.mean(self.data)

    @property
    def stddev(self):
        return statistics.stdev(self.data)

    @property
    def rounds(self):
        return len(self.data)

    @property
    def median(self):
        return statistics.median(self.data)

    @property
    def iqr(self):
        rounds = self.rounds
        data = sorted(self.data)

        # See: https://en.wikipedia.org/wiki/Quartile#Computing_methods
        if rounds % 2:  # Method 3
            n, q = rounds // 4, rounds % 4
            if q == 1:
                quartile_1 = 0.25 * data[n - 1] + 0.75 * data[n]
                quartile_3 = 0.75 * data[3 * n] + 0.25 * data[3 * n + 1]
            else:
                quartile_1 = 0.75 * data[n] + 0.25 * data[n + 1]
                quartile_3 = 0.25 * data[3 * n + 1] + 0.75 * data[3 * n + 2]
        else:  # Method 2
            quartile_3 = statistics.median(data[rounds // 2:])
            quartile_1 = statistics.median(data[:rounds // 2])
        return quartile_3 - quartile_1
