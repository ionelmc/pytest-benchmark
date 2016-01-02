import json
import os
from itertools import chain
from pathlib import Path

from . import plugin


class Storage(object):
    def __init__(self, path, logger, default_platform=None, hooks=plugin):
        self.path = Path(path)
        self.default_platform = default_platform
        if not self.path.exists():
            self.path.mkdir(parents=True)
        self.path = self.path.resolve()
        self.hooks = hooks
        self.logger = logger
        self._cache = {}

    def __str__(self):
        return str(self.path)

    @property
    def location(self):
        return str(self.path.relative_to(os.getcwd()))

    def get(self, name):
        path = self.path.joinpath(self.default_platform) if self.default_platform else self.path
        if not path.exists():
            path.mkdir(parents=True)
        return path.joinpath(name)

    def query(self, globish):
        candidate = Path(globish)
        if candidate.is_file():
            return [candidate]

        parts = candidate.parts
        if len(parts) > 2:
            raise ValueError("%s isn't an existing file or acceptable glob. "
                             "Expected 'platform-glob/filename-glob' or 'filename-glob'.")
        elif len(parts) == 2:
            platform_glob, filename_glob = parts
        else:
            platform_glob = self.default_platform or '*'
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
        result = []
        for file in self.query(globish):
            if file in self._cache:
                data = self._cache[file]
            else:
                with file.open('rU') as fh:
                    try:
                        data = json.load(fh)
                    except Exception as exc:
                        self.logger.warn("BENCHMARK-C5",
                                         "Failed to load %s: %s" % (file, exc), fslocation=self.location)
                        continue
                self._cache[file] = data

            result.append((file.relative_to(self.path), data))
        return result

