
from .base_report_backend import BaseReportBackend

from ..storage import Storage
from ..utils import safe_dumps


class FileReportBackend(BaseReportBackend):
    def __init__(self, config):
        super(FileReportBackend, self).__init__(config)
        self.storage = Storage(config.getoption("benchmark_storage"),
                               default_machine_id=self.machine_id,
                               logger=self.logger)

    @property
    def _next_num(self):
        files = self.storage.query("[0-9][0-9][0-9][0-9]_*")
        files.sort(reverse=True)
        if not files:
            return "0001"
        for f in files:
            try:
                return "%04i" % (int(str(f.name).split('_')[0]) + 1)
            except ValueError:
                raise

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
            with self.json as fh:
                fh.write(safe_dumps(output_json, ensure_ascii=True, indent=4).encode())
            self.logger.info("Wrote benchmark data in: %s" % self.json, purple=True)

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
            output_file = self.storage.get("%s_%s.json" % (self._next_num, save))
            assert not output_file.exists()

            with output_file.open('wb') as fh:
                fh.write(safe_dumps(output_json, ensure_ascii=True, indent=4).encode())
            self.logger.info("Saved benchmark data in: %s" % output_file)

    def handle_loading(self, machine_info):
        compared_mapping = {}
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
                    machine_info=machine_info,
                    compared_benchmark=compared_benchmark,
                )
                compared_mapping[path] = dict(
                    (bench['fullname'], bench) for bench in compared_benchmark['benchmarks']
                )
                self.logger.info("Comparing against benchmarks from: %s" % path)
        return compared_mapping

