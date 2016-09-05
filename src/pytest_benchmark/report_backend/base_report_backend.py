import abc

from ..utils import get_machine_id
from ..logger import Logger


class BaseReportBackend:
    __metaclass__ = abc.ABCMeta

    def __init__(self, config):
        self.verbose = config.getoption("benchmark_verbose")
        self.logger = Logger(self.verbose, config)
        self.config = config
        self.machine_id = get_machine_id()
        self.save = config.getoption("benchmark_save")
        self.autosave = config.getoption("benchmark_autosave")
        self.save_data = config.getoption("benchmark_save_data")
        self.json = config.getoption("benchmark_json")
        self.compare = config.getoption("benchmark_compare")


    @abc.abstractmethod
    def handle_saving(self, benchmarks, machine_info):
        pass

    @abc.abstractmethod
    def handle_loading(self, machine_info):
        pass

