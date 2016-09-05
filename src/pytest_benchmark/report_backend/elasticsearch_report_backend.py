
from elasticsearch import Elasticsearch

from .base_report_backend import BaseReportBackend


class ElasticReportBackend(BaseReportBackend):
    def __init__(self, config):
        self.elasticsearch_host = config.getoption("benchmark_elasticsearch_host")
        self.elasticsearch_index = config.getoption("benchmark_elasticsearch_index")
        self.elasticsearch_doctype = config.getoption("benchmark_elasticsearch_doctype")
        self.elasticsearch = Elasticsearch(self.elasticsearch_host)
        super().__init__(config)

    def handle_saving(self, benchmarks, machine_info):
        save = benchmarks and self.save or self.autosave
        if save:
            commit_info = self.config.hook.pytest_benchmark_generate_commit_info(config=self.config)
            self.config.hook.pytest_benchmark_update_commit_info(config=self.config, commit_info=commit_info)

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
            output_benchmarks = output_json.pop("benchmarks")
            for bench in output_benchmarks:
                # add top level info from output_json dict to each record
                bench.update(output_json)
                self.elasticsearch.index(
                    index=self.elasticsearch_index,
                    doc_type=self.elasticsearch_doctype,
                    body=bench)
            self.logger.info("Saved benchmark data to %s to index %s as doctype %s" %
                             (
                                 self.elasticsearch_host,
                                 self.elasticsearch_index,
                                 self.elasticsearch_doctype
                             )
                             )

    def handle_loading(self, machine_info):
        return {}
