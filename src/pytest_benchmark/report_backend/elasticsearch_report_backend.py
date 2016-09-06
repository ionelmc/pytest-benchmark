from elasticsearch import Elasticsearch

from .base_report_backend import BaseReportBackend
from ..elasticsearch_storage import ElasticsearchStorage


class ElasticReportBackend(BaseReportBackend):
    def __init__(self, config):
        self.elasticsearch_host = config.getoption("benchmark_elasticsearch_host")
        self.elasticsearch_index = config.getoption("benchmark_elasticsearch_index")
        self.elasticsearch_doctype = config.getoption("benchmark_elasticsearch_doctype")
        self.project_name = config.getoption("benchmark_project")
        self.elasticsearch = Elasticsearch(self.elasticsearch_host)
        self._create_index()
        super().__init__(config)
        self.storage = ElasticsearchStorage(self.elasticsearch_host,
                                            self.elasticsearch_index,
                                            self.elasticsearch_doctype,
                                            self.logger,
                                            default_machine_id=self.machine_id)

    def _create_index(self):
        mapping = {
            "mappings": {
                "benchmark": {
                    "properties": {
                        "commit_info": {
                            "properties": {
                                "dirty": {
                                    "type": "boolean"
                                },
                                "id": {
                                    "type": "string",
                                    "index": "not_analyzed"

                                },
                                "project": {
                                    "type": "string",
                                    "index": "not_analyzed"
                                }
                            }
                        },
                        "datetime": {
                            "type": "date",
                            "format": "strict_date_optional_time||epoch_millis"
                        },
                        "name": {
                            "type": "string",
                            "index": "not_analyzed"
                        },
                        "fullname": {
                            "type": "string",
                            "index": "not_analyzed"
                        },
                        "version": {
                            "type": "string",
                            "index": "not_analyzed"
                        },
                        "machine_info": {
                            "properties": {
                                "machine": {
                                    "type": "string",
                                    "index": "not_analyzed"
                                },
                                "node": {
                                    "type": "string",
                                    "index": "not_analyzed"
                                },
                                "processor": {
                                    "type": "string",
                                    "index": "not_analyzed"
                                },
                                "python_build": {
                                    "type": "string",
                                    "index": "not_analyzed"
                                },
                                "python_compiler": {
                                    "type": "string",
                                    "index": "not_analyzed"
                                },
                                "python_implementation": {
                                    "type": "string",
                                    "index": "not_analyzed"
                                },
                                "python_implementation_version": {
                                    "type": "string",
                                    "index": "not_analyzed"
                                },
                                "python_version": {
                                    "type": "string",
                                    "index": "not_analyzed"
                                },
                                "release": {
                                    "type": "string",
                                    "index": "not_analyzed"
                                },
                                "system": {
                                    "type": "string",
                                    "index": "not_analyzed"
                                }
                            }
                        },
                        "options": {
                            "properties": {
                                "disable_gc": {
                                    "type": "boolean"
                                },
                                "max_time": {
                                    "type": "double"
                                },
                                "min_rounds": {
                                    "type": "long"
                                },
                                "min_time": {
                                    "type": "double"
                                },
                                "timer": {
                                    "type": "string"
                                },
                                "warmup": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "stats": {
                            "properties": {
                                "hd15iqr": {
                                    "type": "double"
                                },
                                "iqr": {
                                    "type": "double"
                                },
                                "iqr_outliers": {
                                    "type": "long"
                                },
                                "iterations": {
                                    "type": "long"
                                },
                                "ld15iqr": {
                                    "type": "double"
                                },
                                "max": {
                                    "type": "double"
                                },
                                "mean": {
                                    "type": "double"
                                },
                                "median": {
                                    "type": "double"
                                },
                                "min": {
                                    "type": "double"
                                },
                                "outliers": {
                                    "type": "string"
                                },
                                "q1": {
                                    "type": "double"
                                },
                                "q3": {
                                    "type": "double"
                                },
                                "rounds": {
                                    "type": "long"
                                },
                                "stddev": {
                                    "type": "double"
                                },
                                "stddev_outliers": {
                                    "type": "long"
                                }
                            }
                        },
                    }
                }
            }
        }
        self.elasticsearch.indices.create(index=self.elasticsearch_index, ignore=400, body=mapping)

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
                doc_id = "%s_%s" % (save, bench["fullname"])
                self.elasticsearch.index(
                    index=self.elasticsearch_index,
                    doc_type=self.elasticsearch_doctype,
                    body=bench,
                    id=doc_id,
                )
            self.logger.info("Saved benchmark data to %s to index %s as doctype %s" %
                             (
                                 self.elasticsearch_host,
                                 self.elasticsearch_index,
                                 self.elasticsearch_doctype
                             )
                             )

    def handle_loading(self, machine_info):
        compared_mapping = {}
        if self.compare:
            compared_benchmarks = list(self.storage.load(self.project_name))[-1:]

            if not compared_benchmarks:
                msg = "Can't compare. No benchmark records in project %s in elastic %s." % (self.project_name, self.storage.location)
                code = "BENCHMARK-C1"
                self.logger.warn(code, msg, fslocation=self.storage.location)

            for commit_time, compared_benchmark in compared_benchmarks:
                self.config.hook.pytest_benchmark_compare_machine_info(
                    config=self.config,
                    benchmarksession=self,
                    machine_info=machine_info,
                    compared_benchmark=compared_benchmark,
                )
                compared_mapping[commit_time] = dict(
                    (bench['fullname'], bench) for bench in compared_benchmark['benchmarks']
                )
                self.logger.info("Comparing against benchmarks from: %s" % commit_time)

        return compared_mapping
