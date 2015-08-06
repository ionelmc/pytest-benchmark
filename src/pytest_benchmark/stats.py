from __future__ import division

import math
import statistics


class RunningStats(object):
    # implementation of http://www.johndcook.com/standard_deviation.html
    fields = "min", "max", "mean", "stddev", "rounds",

    def __init__(self):
        self.rounds = 0
        self.total = 0
        self.min = float('inf')
        self.max = 0
        self.__old_mean = self.__new_mean = self.__old_exp = self.__new_exp = None

    def update(self, duration):
        self.total += duration
        self.min = min(duration, self.min)
        self.max = max(duration, self.max)
        self.rounds += 1
        if self.rounds == 1:
            self.__old_mean = self.__new_mean = duration
            self.__old_exp = 0.0
        else:
            delta = duration - self.__old_mean
            self.__new_mean = self.__old_mean + delta / self.rounds
            self.__new_exp = self.__old_exp + delta * (duration - self.__new_mean)

            self.__old_mean = self.__new_mean
            self.__old_exp = self.__new_exp

    @property
    def mean(self):
        # see:
        #  http://stackoverflow.com/questions/1174984/how-to-efficiently-calculate-a-running-standard-deviation
        #  http://www.johndcook.com/blog/standard_deviation/
        return self.__new_mean if self.rounds else 0.0

    @property
    def variance(self):
        return self.__new_exp / (self.rounds - 1) if self.rounds > 1 else 0.0

    @property
    def stddev(self):
        return math.sqrt(self.variance)

    def __str__(self):
        return "Stats[%s rounds in %.4fsec, min=%.4fsec, max=%.4fsec, mean=%.4fsec, stddev=%.4fsec]" % (
            self.rounds, self.total, self.min, self.max, self.mean, self.stddev
        )


class AdvancedStats(object):
    fields = "min", "max", "mean", "stddev", "rounds",

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
