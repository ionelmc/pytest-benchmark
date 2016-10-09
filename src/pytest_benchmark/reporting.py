from .logger import Logger
from .utils import get_machine_id
from .utils import safe_dumps


class Reporter(object):
    def __init__(self, config, storage):
        self.verbose = config.getoption("benchmark_verbose")
        self.logger = Logger(self.verbose, config)
        self.config = config
        self.machine_id = get_machine_id()
        self.save = config.getoption("benchmark_save")
        self.autosave = config.getoption("benchmark_autosave")
        self.save_data = config.getoption("benchmark_save_data")
        self.json = config.getoption("benchmark_json")
        self.compare = config.getoption("benchmark_compare")
        self.storage = storage

    def save_json(self, output_json):
        with self.json as fh:
            fh.write(safe_dumps(output_json, ensure_ascii=True, indent=4).encode())
        self.logger.info("Wrote benchmark data in: %s" % self.json, purple=True)

    def handle_saving(self, benchmarks, machine_info):
        save = benchmarks and self.save or self.autosave
        if save or self.json:
            commit_info = self.config.hook.pytest_benchmark_generate_commit_info(config=self.config)
            self.config.hook.pytest_benchmark_update_commit_info(config=self.config, commit_info=commit_info)

        if self.json:
            output_json = self.config.hook.pytest_benchmark_generate_json(
                config=self.config,
                benchmarks=benchmarks,
                include_data=True,
                machine_info=machine_info,
                commit_info=commit_info,
            )
            self.config.hook.pytest_benchmark_update_json(
                config=self.config,
                benchmarks=benchmarks,
                output_json=output_json,
            )
            self.save_json(output_json)

        if save:
            output_json = self.config.hook.pytest_benchmark_generate_json(
                config=self.config,
                benchmarks=benchmarks,
                include_data=self.save_data,
                machine_info=machine_info,
                commit_info=commit_info,
            )
            self.config.hook.pytest_benchmark_update_json(
                config=self.config,
                benchmarks=benchmarks,
                output_json=output_json,
            )
            self.storage.save(output_json, save)

    def handle_loading(self, machine_info):
        compared_mapping = {}
        if self.compare:
            if self.compare is True:
                compared_benchmarks = list(self.storage.load())[-1:]
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
                    machine_info=machine_info,
                    compared_benchmark=compared_benchmark,
                )
                compared_mapping[path] = dict(
                    (bench['fullname'], bench) for bench in compared_benchmark['benchmarks']
                )
                self.logger.info("Comparing against benchmarks from: %s" % path)
        return compared_mapping

