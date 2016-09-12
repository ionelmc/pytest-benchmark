
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

    def _save(self, output_json, save):
        output_file = self.storage.get("%s_%s.json" % (self._next_num, save))
        self.logger.info("output_file " + str(output_file))
        self.logger.info("save " + str(save))
        assert not output_file.exists()
        with output_file.open('wb') as fh:
            fh.write(safe_dumps(output_json, ensure_ascii=True, indent=4).encode())
        self.logger.info("Saved benchmark data in: %s" % output_file)

    def _load(self, id_prefix=None):
        if id_prefix is None:
            return self.storage.load('[0-9][0-9][0-9][0-9]_')
        else:
            return self.storage.load(id_prefix)

