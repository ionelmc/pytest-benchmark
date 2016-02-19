from __future__ import absolute_import

import csv
import operator


class CSVResults(object):
    def __init__(self, columns, sort):
        self.columns = columns
        self.sort = sort

    def render(self, stream, groups):
        writer = csv.writer(stream)
        params = sorted(set(
            param
            for group, benchmarks in groups
            for benchmark in benchmarks
            for param in benchmark["params"]
        ))
        writer.writerow([
            "name",
        ] + [
            "param:{0}".format(p)
            for p in params
        ] + self.columns)

        for group, benchmarks in groups:
            benchmarks = sorted(benchmarks, key=operator.itemgetter(self.sort))

            for bench in benchmarks:
                row = [bench.get("fullfunc", bench["fullname"])]
                row.extend(bench['params'].get(param, "") for param in params)
                row.extend(bench[prop] for prop in self.columns)
                writer.writerow(row)
