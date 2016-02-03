import json
import os
from itertools import chain

from pathlib import Path

from .utils import short_filename, annotate_source


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

    def query(self, *globs_or_files):
        files = []
        globs = []
        if not globs_or_files:
            globs_or_files = "*",

        for globish in globs_or_files:
            candidate = Path(globish)
            try:
                is_file = candidate.is_file()
            except OSError:
                is_file = False
            if is_file:
                files.append(candidate)
                continue

            parts = candidate.parts
            if len(parts) > 2:
                raise ValueError("{0!r} isn't an existing file or acceptable glob. "
                                 "Expected 'platform-glob/filename-glob' or 'filename-glob'.".format(globish))
            elif len(parts) == 2:
                platform_glob, filename_glob = parts
            else:
                platform_glob = self.default_machine_id or "*"
                filename_glob, = parts or ['']

            filename_glob = filename_glob.rstrip("*") + "*.json"
            globs.append((platform_glob, filename_glob))

        return sorted(chain(
            files,
            (
                file
                for platform_glob, filename_glob in globs
                for path in self.path.glob(platform_glob)
                for file in path.glob(filename_glob)
            ), (
                file for file in self.path.glob(filename_glob)
            )
        ), key=lambda file: (file.name, file.parent))

    def load(self, *globs_or_files):
        for file in self.query(*globs_or_files):
            if file in self._cache:
                data = self._cache[file]
            else:
                with file.open("rU") as fh:
                    try:
                        data = json.load(fh)
                    except Exception as exc:
                        self.logger.warn("BENCHMARK-C5",
                                         "Failed to load {0}: {1}".format(file, exc), fslocation=self.location)
                        continue
                self._cache[file] = data

            yield file.relative_to(self.path), data

    def load_benchmarks(self, *globs_or_files):
        for path, data in self.load(*globs_or_files):
            source = short_filename(path)

            for bench in data["benchmarks"]:
                bench.update(bench.pop("stats"))
                bench['path'] = str(path)
                yield annotate_source(bench, source)
