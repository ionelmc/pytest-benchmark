"""
Don't use cached_property because we want a typing for getter and setter,
and we can't use iqr_outliers.setter with cached_property because Python apply the
decorator on cached_property and not on the property.
"""

from __future__ import division
from __future__ import print_function

import operator
import statistics
from bisect import bisect_left
from bisect import bisect_right

from .utils import funcname
from .utils import get_cprofile_functions


class Stats(object):
    fields = (
        "min", "max", "mean", "stddev", "rounds", "median", "iqr", "q1", "q3", "iqr_outliers", "stddev_outliers",
        "outliers", "ld15iqr", "hd15iqr", "ops", "total"
    )

    def __init__(self):
        self.data = []
        self.cache = {}

    def __bool__(self):
        return bool(self.data)

    def __nonzero__(self):
        return bool(self.data)

    def as_dict(self):
        return dict(
            (field, getattr(self, field))
            for field in self.fields
        )

    def update(self, duration):
        self.data.append(duration)

    @property
    def sorted_data(self):
        return sorted(self.data)

    @property
    def total(self) -> float or int:
        """ Return the total time of round / iterations."""
        cache_value = self.cache.get('total')

        if cache_value is not None:
            return cache_value

        return sum(self.data)

    @total.setter
    def total(self, value: float or int) -> None:
        """ Set the total time of round / iterations."""
        self.cache['total'] = value

    @property
    def min(self) -> float or int:
        """ Return the minimum observed time of round / iterations."""
        cache_value = self.cache.get('min')

        if cache_value is not None:
            return cache_value

        return min(self.data)

    @min.setter
    def min(self, value: float or int) -> None:
        """ Set the minimum observed time of round / iterations."""
        self.cache['min'] = value

    @property
    def max(self) -> float or int:
        """ Return the maximum observed time of round / iterations"""
        cache_value = self.cache.get('max')

        if cache_value is not None:
            return cache_value

        return max(self.data)

    @max.setter
    def max(self, value: float or int) -> None:
        """ Set the maximum observed time of round / iterations."""
        self.cache['max'] = value

    @property
    def mean(self) -> float or int:
        """ Return the mean of time of round / iterations."""
        cache_value = self.cache.get('mean')

        if cache_value is not None:
            return cache_value

        return statistics.mean(self.data)

    @mean.setter
    def mean(self, value: float or int) -> None:
        """ Set the mean. """
        self.cache['mean'] = value

    @property
    def stddev(self) -> float or int:
        """ Return the standard deviation. """
        cache_value = self.cache.get('stddev')

        if cache_value is not None:
            return cache_value

        if len(self.data) > 1:
            return statistics.stdev(self.data)
        else:
            return 0

    @stddev.setter
    def stddev(self, value: float or int) -> None:
        """ Set the standard deviation. """
        self.cache['stddev'] = value

    @property
    def stddev_outliers(self) -> float or int:
        """
        Return the number of outliers (StdDev-style).

        Notes:
            Count of StdDev outliers: what's beyond (Mean - StdDev, Mean - StdDev)
        """
        cache_value = self.cache.get('stddev_outliers')

        if cache_value is not None:
            return cache_value

        count = 0
        q0 = self.mean - self.stddev
        q4 = self.mean + self.stddev
        for val in self.data:
            if val < q0 or val > q4:
                count += 1
        return count

    @stddev_outliers.setter
    def stddev_outliers(self, value: str) -> None:
        """ Set the number of outliers. """
        self.cache['stddev_outliers'] = value

    @property
    def rounds(self) -> float or int:
        """ Return the number of rounds, can't be changed by setter."""
        return len(self.data)

    @property
    def median(self) -> float or int:
        """ Return the median of time of round / iterations. """
        cache_value = self.cache.get('median')

        if cache_value is not None:
            return cache_value

        return statistics.median(self.data)

    @median.setter
    def median(self, value: float or int) -> None:
        """ Set the median of time of round / iterations."""
        self.cache['median'] = value

    @property
    def ld15iqr(self) -> float or int:
        """ Return the lowest datum within 1.5 IQR under Q1 (Tukey-style). """
        cache_value = self.cache.get('ld15iqr')

        if cache_value is not None:
            return cache_value

        if len(self.data) == 1:
            return self.data[0]
        else:
            return self.sorted_data[bisect_left(self.sorted_data, self.q1 - 1.5 * self.iqr)]

    @ld15iqr.setter
    def ld15iqr(self, value: int or float) -> None:
        """ Set the lowest datum within 1.5 IQR under Q1 (Tukey-style). """
        self.cache['ld15iqr'] = value

    @property
    def hd15iqr(self) -> float or int:
        """ Return the highest datum within 1.5 IQR over Q3 (Tukey-style). """
        cache_value = self.cache.get('hd15iqr')

        if cache_value is not None:
            return cache_value

        if len(self.data) == 1:
            return self.data[0]
        else:
            pos = bisect_right(self.sorted_data, self.q3 + 1.5 * self.iqr)
            if pos == len(self.data):
                return self.sorted_data[-1]
            else:
                return self.sorted_data[pos]

    @hd15iqr.setter
    def hd15iqr(self, value: int or float) -> None:
        """ Set the highest datum within 1.5 IQR over Q3 (Tukey-style). """
        self.cache['hd15iqr'] = value

    @property
    def q1(self) -> float or int:
        """ Return the first quartile. """
        cache_value = self.cache.get('q1')

        if cache_value is not None:
            return cache_value

        rounds = self.rounds
        data = self.sorted_data

        # See: https://en.wikipedia.org/wiki/Quartile#Computing_methods
        if rounds == 1:
            return data[0]
        elif rounds % 2:  # Method 3
            n, q = rounds // 4, rounds % 4
            if q == 1:
                return 0.25 * data[n - 1] + 0.75 * data[n]
            else:
                return 0.75 * data[n] + 0.25 * data[n + 1]
        else:  # Method 2
            return statistics.median(data[:rounds // 2])

    @q1.setter
    def q1(self, value: int or float) -> None:
        """ Set the first quartile. """
        self.cache['q1'] = value

    @property
    def q3(self) -> float or int:
        """ Return the third quartile. """
        cache_value = self.cache.get('q3')

        if cache_value is not None:
            return cache_value

        rounds = self.rounds
        data = self.sorted_data

        # See: https://en.wikipedia.org/wiki/Quartile#Computing_methods
        if rounds == 1:
            return data[0]
        elif rounds % 2:  # Method 3
            n, q = rounds // 4, rounds % 4
            if q == 1:
                return 0.75 * data[3 * n] + 0.25 * data[3 * n + 1]
            else:
                return 0.25 * data[3 * n + 1] + 0.75 * data[3 * n + 2]
        else:  # Method 2
            return statistics.median(data[rounds // 2:])

    @q3.setter
    def q3(self, value: int or float) -> None:
        """ Set the third quartile. """
        self.cache['q3'] = value

    @property
    def iqr(self) -> float or int:
        """ Return the interquartile range. """
        cache_value = self.cache.get('iqr')

        if cache_value is not None:
            return cache_value

        return self.q3 - self.q1

    @iqr.setter
    def iqr(self, value) -> None:
        """ Set the interquartile range. """
        self.cache['iqr'] = value

    @property
    def iqr_outliers(self) -> float or int:
        """
        Return the number of outliers (Tukey-style).

        Notes:
            Count of Tukey outliers: what's beyond (Q1 - 1.5IQR, Q3 + 1.5IQR)
        """
        cache_value = self.cache.get('iqr_outliers')

        if cache_value is not None:
            return cache_value

        count = 0
        q0 = self.q1 - 1.5 * self.iqr
        q4 = self.q3 + 1.5 * self.iqr
        for val in self.data:
            if val < q0 or val > q4:
                count += 1
        return count

    @iqr_outliers.setter
    def iqr_outliers(self, value: str) -> None:
        """ Set the number of outliers. """
        self.cache['iqr_outliers'] = value

    @property
    def outliers(self) -> str:
        """
        Return the number of outliers.

        Notes:
            This is a string because it is used in a template.
            The separator is a semicolon ';' because it is used in a template.
        """

        cache_value = self.cache.get('outliers')

        if cache_value is not None:
            return cache_value

        return "%s;%s" % (self.stddev_outliers, self.iqr_outliers)

    @outliers.setter
    def outliers(self, value: str) -> None:
        """ Set the number of outliers. """
        self.cache['outliers'] = value

    @property
    def ops(self) -> float or int:
        """ Return the average of operations per second of round / iterations."""
        cache_value = self.cache.get('ops')

        if cache_value is not None:
            return cache_value

        if self.total:
            return self.rounds / self.total
        return 0

    @ops.setter
    def ops(self, value: float or int) -> None:
        """Set the average of operations per second of round / iterations."""
        self.cache['ops'] = value


class Metadata(object):
    def __init__(self, fixture, iterations, options):
        self.name = fixture.name
        self.fullname = fixture.fullname
        self.group = fixture.group
        self.param = fixture.param
        self.params = fixture.params
        self.extra_info = fixture.extra_info
        self.cprofile_stats = fixture.cprofile_stats

        self.iterations = iterations
        self.stats = Stats()
        self.options = options
        self.fixture = fixture

    def __bool__(self):
        return bool(self.stats)

    def __nonzero__(self):
        return bool(self.stats)

    def get(self, key, default=None):
        try:
            return getattr(self.stats, key)
        except AttributeError:
            return getattr(self, key, default)

    def __getitem__(self, key):
        try:
            return getattr(self.stats, key)
        except AttributeError:
            return getattr(self, key)

    @property
    def has_error(self):
        return self.fixture.has_error

    def as_dict(self, include_data=True, flat=False, stats=True, cprofile=None):
        result = {
            "group": self.group,
            "name": self.name,
            "fullname": self.fullname,
            "params": self.params,
            "param": self.param,
            "extra_info": self.extra_info,
            "options": dict(
                (k, funcname(v) if callable(v) else v) for k, v in self.options.items()
            )
        }
        if self.cprofile_stats:
            cprofile_list = result["cprofile"] = []
            cprofile_functions = get_cprofile_functions(self.cprofile_stats)
            stats_columns = ["cumtime", "tottime", "ncalls", "ncalls_recursion",
                             "tottime_per", "cumtime_per", "function_name"]
            # move column first
            if cprofile is not None:
                stats_columns.remove(cprofile)
                stats_columns.insert(0, cprofile)
            for column in stats_columns:
                cprofile_functions.sort(key=operator.itemgetter(column), reverse=True)
                for cprofile_function in cprofile_functions[:25]:
                    if cprofile_function not in cprofile_list:
                        cprofile_list.append(cprofile_function)
                # if we want only one column or we already have all available functions
                if cprofile is None or len(cprofile_functions) == len(cprofile_list):
                    break
        if stats:
            stats = self.stats.as_dict()
            if include_data:
                stats["data"] = self.stats.data
            stats["iterations"] = self.iterations
            if flat:
                result.update(stats)
            else:
                result["stats"] = stats
        return result

    def update(self, duration):
        self.stats.update(duration / self.iterations)


def normalize_stats(stats):
    if 'ops' not in stats:
        # fill field added in 3.1.0
        stats['ops'] = 1 / stats['mean']
    return stats
