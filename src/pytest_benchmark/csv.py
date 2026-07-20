"""
..
  PYTEST_DONT_REWRITE
"""

import csv
import operator
from pathlib import Path
from typing import Any
from typing import cast

from .logger import Logger


class CSVResults:
    def __init__(self, columns: list[str], sort: str, logger: Logger) -> None:
        self.columns = columns
        self.sort = sort
        self.logger = logger

    def render(
        self,
        output_file: str | Path,
        groups: list[tuple[str, list[dict[str, Any]]]],
    ) -> None:
        output_file = Path(output_file)
        output_file.parent.mkdir(exist_ok=True, parents=True)

        if not output_file.suffix:
            output_file = output_file.with_suffix('.csv')

        with output_file.open('w') as stream:
            writer = csv.writer(stream)
            params = sorted(
                {param for group, benchmarks in groups for benchmark in benchmarks for param in benchmark.get('params', {}) or ()}
            )
            writer.writerow(
                [
                    'name',
                ]
                + [f'param:{p}' for p in params]
                + self.columns
            )

            for _, benchmarks in groups:
                benchmarks = sorted(benchmarks, key=operator.itemgetter(self.sort))

                for bench in benchmarks:
                    row = [bench.get('fullfunc', bench['fullname'])]
                    bench_params = cast(dict[str, object] | None, bench.get('params', {}))
                    bench_params = bench_params if bench_params is not None else {}
                    row.extend(bench_params.get(param, '') for param in params)
                    row.extend(bench[prop] for prop in self.columns)
                    writer.writerow(row)

        self.logger.info(f'Generated csv: {output_file}', bold=True)
