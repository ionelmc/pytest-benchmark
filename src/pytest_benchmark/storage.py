import json
import os
from itertools import chain

from pathlib import Path

from pytest_benchmark.utils import short_filename


class Storage(object):
    def __init__(self, path, logger, default_machine_id=None):
        self.path = Path(path)
        self.default_machine_id = default_machine_id
        if not self.path.exists():
            self.path.mkdir(parents=True)
        self.path = self.path.resolve()
        self.logger = logger
        self._cache = {}

    def __str__(self):
        return str(self.path)

    @property
    def location(self):
        return str(self.path.relative_to(os.getcwd()))

    def get(self, name):
        path = self.path.joinpath(self.default_machine_id) if self.default_machine_id else self.path
        if not path.exists():
            path.mkdir(parents=True)
        return path.joinpath(name)

    def query(self, globish):
        candidate = Path(globish)
        if candidate.is_file():
            return [candidate]

        parts = candidate.parts
        if len(parts) > 2:
            raise ValueError("{0!r} isn't an existing file or acceptable glob. "
                             "Expected 'platform-glob/filename-glob' or 'filename-glob'.".format(globish))
        elif len(parts) == 2:
            platform_glob, filename_glob = parts
        else:
            platform_glob = self.default_machine_id or '*'
            filename_glob, = parts or ['']

        filename_glob = filename_glob.rstrip('*') + '*.json'

        return sorted(chain((
            file
            for path in self.path.glob(platform_glob)
            for file in path.glob(filename_glob)
        ), (
            file for file in self.path.glob(filename_glob)
        )), key=lambda file: (file.name, file.parent))

    def load(self, globish):
        for file in self.query(globish):
            if file in self._cache:
                data = self._cache[file]
            else:
                with file.open('rU') as fh:
                    try:
                        data = json.load(fh)
                    except Exception as exc:
                        self.logger.warn("BENCHMARK-C5",
                                         "Failed to load {0}: {1}".format(file, exc), fslocation=self.location)
                        continue
                self._cache[file] = data

            yield file.relative_to(self.path), data

    def load_benchmarks(self, globish):
        for path, data in self.load(globish):
            source = short_filename(path)

            for bench in data['benchmarks']:
                yield dict(
                    bench["stats"],
                    name="{0} ({1})".format(bench.name, source),
                    fullname="{0} ({1})".format(bench.fullname, source),
                    path=str(path),
                    source=source,
                )
