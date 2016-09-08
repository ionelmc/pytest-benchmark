from __future__ import division
from __future__ import print_function

import pytest

from .fixture import statistics
from .fixture import statistics_error
from .logger import Logger
from .storage import Storage
from .table import TableResults
from .utils import NAME_FORMATTERS
from .utils import SecondsDecimal
from .utils import cached_property
from .utils import first_or_value
from .utils import get_machine_id
from .utils import load_timer
from .utils import safe_dumps
from .utils import short_filename


class PerformanceRegression(pytest.UsageError):
    pass


class BenchmarkSession(object):
    compared_mapping = None
    groups = None

    def __init__(self, config):
        self.verbose = config.getoption("benchmark_verbose")
        self.logger = Logger(self.verbose, config)
        self.config = config
        self.performance_regressions = []
        self.benchmarks = []
        self.machine_id = get_machine_id()

        self.options = dict(
            min_time=SecondsDecimal(config.getoption("benchmark_min_time")),
            min_rounds=config.getoption("benchmark_min_rounds"),
            max_time=SecondsDecimal(config.getoption("benchmark_max_time")),
            timer=load_timer(config.getoption("benchmark_timer")),
            calibration_precision=config.getoption("benchmark_calibration_precision"),
            disable_gc=config.getoption("benchmark_disable_gc"),
            warmup=config.getoption("benchmark_warmup"),
            warmup_iterations=config.getoption("benchmark_warmup_iterations"),
            use_cprofile=config.getoption("benchmark_cprofile"),
        )
        self.skip = config.getoption("benchmark_skip")
        self.disabled = config.getoption("benchmark_disable") and not config.getoption("benchmark_enable")

        if config.getoption("dist", "no") != "no" and not self.skip:
            self.logger.warn(
                "BENCHMARK-U2",
                "Benchmarks are automatically disabled because xdist plugin is active."
                "Benchmarks cannot be performed reliably in a parallelized environment.",
                fslocation="::"
            )
            self.disabled = True
        if hasattr(config, "slaveinput"):
            self.disabled = True
        if not statistics:
            self.logger.warn(
                "BENCHMARK-U3",
                "Benchmarks are automatically disabled because we could not import `statistics`\n\n%s" %
                statistics_error,
                fslocation="::"
            )
            self.disabled = True

        self.only = config.getoption("benchmark_only")
        self.sort = config.getoption("benchmark_sort")
        self.columns = config.getoption("benchmark_columns")
        if self.skip and self.only:
            raise pytest.UsageError("Can't have both --benchmark-only and --benchmark-skip options.")
        if self.disabled and self.only:
            raise pytest.UsageError(
                "Can't have both --benchmark-only and --benchmark-disable options. Note that --benchmark-disable is "
                "automatically activated if xdist is on or you're missing the statistics dependency.")
        self.group_by = config.getoption("benchmark_group_by")
        self.save = config.getoption("benchmark_save")
        self.autosave = config.getoption("benchmark_autosave")
        self.save_data = config.getoption("benchmark_save_data")
        self.json = config.getoption("benchmark_json")
        self.compare = config.getoption("benchmark_compare")
        self.compare_fail = config.getoption("benchmark_compare_fail")
        self.name_format = NAME_FORMATTERS[config.getoption("benchmark_name")]

        self.storage = Storage(config.getoption("benchmark_storage"),
                               default_machine_id=self.machine_id, logger=self.logger)
        self.histogram = first_or_value(config.getoption("benchmark_histogram"), False)

    @cached_property
    def machine_info(self):
        obj = self.config.hook.pytest_benchmark_generate_machine_info(config=self.config)
        self.config.hook.pytest_benchmark_update_machine_info(
            config=self.config,
            machine_info=obj
        )
        return obj

    def prepare_benchmarks(self):
        for bench in self.benchmarks:
            if bench:
                compared = False
                for path, compared_mapping in self.compared_mapping.items():
                    if bench.fullname in compared_mapping:
                        compared = compared_mapping[bench.fullname]
                        source = short_filename(path, self.machine_id)
                        flat_bench = bench.as_dict(include_data=False, stats=False)
                        flat_bench.update(compared["stats"])
                        flat_bench["path"] = str(path)
                        flat_bench["source"] = source
                        if self.compare_fail:
                            for check in self.compare_fail:
                                fail = check.fails(bench, flat_bench)
                                if fail:
                                    self.performance_regressions.append((self.name_format(flat_bench), fail))
                        yield flat_bench
                flat_bench = bench.as_dict(include_data=False, flat=True)
                flat_bench["path"] = None
                flat_bench["source"] = compared and "NOW"
                yield flat_bench

    @property
    def next_num(self):
        files = self.storage.query("[0-9][0-9][0-9][0-9]_*")
        files.sort(reverse=True)
        if not files:
            return "0001"
        for f in files:
            try:
                return "%04i" % (int(str(f.name).split('_')[0]) + 1)
            except ValueError:
                raise

    def handle_saving(self):
        save = self.benchmarks and self.save or self.autosave
        if save or self.json:
            commit_info = self.config.hook.pytest_benchmark_generate_commit_info(config=self.config)
            self.config.hook.pytest_benchmark_update_commit_info(config=self.config, commit_info=commit_info)

        if self.json:
            output_json = self.config.hook.pytest_benchmark_generate_json(
                config=self.config,
                benchmarks=self.benchmarks,
                include_data=True,
                machine_info=self.machine_info,
                commit_info=commit_info,
            )
            self.config.hook.pytest_benchmark_update_json(
                config=self.config,
                benchmarks=self.benchmarks,
                output_json=output_json,
            )
            with self.json as fh:
                fh.write(safe_dumps(output_json, ensure_ascii=True, indent=4).encode())
            self.logger.info("Wrote benchmark data in: %s" % self.json, purple=True)

        if save:
            output_json = self.config.hook.pytest_benchmark_generate_json(
                config=self.config,
                benchmarks=self.benchmarks,
                include_data=self.save_data,
                machine_info=self.machine_info,
                commit_info=commit_info,
            )
            self.config.hook.pytest_benchmark_update_json(
                config=self.config,
                benchmarks=self.benchmarks,
                output_json=output_json,
            )
            output_file = self.storage.get("%s_%s.json" % (self.next_num, save))
            assert not output_file.exists()

            with output_file.open('wb') as fh:
                fh.write(safe_dumps(output_json, ensure_ascii=True, indent=4).encode())
            self.logger.info("Saved benchmark data in: %s" % output_file)

    def handle_loading(self):
        self.compared_mapping = {}
        if self.compare:
            if self.compare is True:
                compared_benchmarks = list(self.storage.load('[0-9][0-9][0-9][0-9]_'))[-1:]
            else:
                compared_benchmarks = list(self.storage.load(self.compare))

            if not compared_benchmarks:
                msg = "Can't compare. No benchmark files in %r" % str(self.storage)
                if self.compare is True:
                    msg += ". Can't load the previous benchmark."
                    code = "BENCHMARK-C2"
                else:
                    msg += " match %r." % self.compare
                    code = "BENCHMARK-C1"
                self.logger.warn(code, msg, fslocation=self.storage.location)

            for path, compared_benchmark in compared_benchmarks:
                self.config.hook.pytest_benchmark_compare_machine_info(
                    config=self.config,
                    benchmarksession=self,
                    machine_info=self.machine_info,
                    compared_benchmark=compared_benchmark,
                )
                self.compared_mapping[path] = dict(
                    (bench['fullname'], bench) for bench in compared_benchmark['benchmarks']
                )
                self.logger.info("Comparing against benchmarks from: %s" % path)

    def finish(self):
        self.handle_saving()
        self.handle_loading()
        prepared_benchmarks = list(self.prepare_benchmarks())
        if prepared_benchmarks:
            self.groups = self.config.hook.pytest_benchmark_group_stats(
                config=self.config,
                benchmarks=prepared_benchmarks,
                group_by=self.group_by
            )

    def display(self, tr):
        if not self.groups:
            return

        tr.ensure_newline()
        results_table = TableResults(
            columns=self.columns,
            sort=self.sort,
            histogram=self.histogram,
            name_format=self.name_format,
            logger=self.logger
        )
        results_table.display(tr, self.groups)
        self.check_regressions()

    def check_regressions(self):
        if self.compare_fail and not self.compared_mapping:
            raise pytest.UsageError("--benchmark-compare-fail requires valid --benchmark-compare.")

        if self.performance_regressions:
            self.logger.error("Performance has regressed:\n%s" % "\n".join(
                "\t%s - %s" % line for line in self.performance_regressions
            ))
            raise PerformanceRegression("Performance has regressed.")
