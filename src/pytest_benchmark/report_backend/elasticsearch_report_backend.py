from .base_report_backend import BaseReportBackend
from ..elasticsearch_storage import ElasticsearchStorage


class ElasticReportBackend(BaseReportBackend):
    def __init__(self, config):
        self.elasticsearch_hosts = config.getoption("benchmark_elasticsearch_hosts")
        self.elasticsearch_index = config.getoption("benchmark_elasticsearch_index")
        self.elasticsearch_doctype = config.getoption("benchmark_elasticsearch_doctype")
        self.project_name = config.getoption("benchmark_project_name")
        super(ElasticReportBackend, self).__init__(config)
        self.storage = ElasticsearchStorage(self.elasticsearch_hosts,
                                            self.elasticsearch_index,
                                            self.elasticsearch_doctype,
                                            self.logger,
                                            default_machine_id=self.machine_id)

    def _save(self, output_json, save):
        output_benchmarks = output_json.pop("benchmarks")
        for bench in output_benchmarks:
            # add top level info from output_json dict to each record
            bench.update(output_json)
            doc_id = "%s_%s" % (save, bench["fullname"])
            self.storage.save(bench, doc_id)
        self.logger.info("Saved benchmark data to %s to index %s as doctype %s" %
                         (
                             self.elasticsearch_hosts,
                             self.elasticsearch_index,
                             self.elasticsearch_doctype
                         )
                         )

    def _load(self, id_prefix=None):
        return self.storage.load(self.project_name, id_prefix)
