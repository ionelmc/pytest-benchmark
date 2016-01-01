import os
from itertools import chain
from pathlib import Path


class Storage(object):
    def __init__(self, path, default_platform=None):
        self.path = Path(path)
        self.default_platform = default_platform
        if not self.path.exists():
            self.path.mkdir(parents=True)
        self.path = self.path.resolve()

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
        )))
