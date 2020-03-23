from __future__ import absolute_import

import os
import re
import sys
import json

from ..stats import normalize_stats
from ..utils import Path
from ..utils import urlparse
from ..utils import commonpath
from ..utils import safe_dumps
from ..utils import short_filename

from ..compat import reraise

try:
    from boto3.session import Session as boto3_session
    from botocore.exceptions import ClientError
except ImportError as exc:
    reraise(ImportError, ImportError("Please install boto3 or pytest-benchmark[s3]", exc.args),
            sys.exc_info()[2])


class S3Storage(object):
    def __init__(self, path, logger, client=None, default_machine_id=None):
        self.store = urlparse(path)
        self.bucket = self.store.netloc
        self.path = Path(self.store.path.strip("/"))
        self.default_machine_id = default_machine_id
        if not client:
            session = boto3_session()
            client = session.client("s3")
        self.client = client
        self.logger = logger
        self._cache = {}

    def __str__(self):
        return self.store.geturl()

    @property
    def location(self):
        return self.store.geturl()

    def get(self, name):
        path = self.path.joinpath(self.default_machine_id) if self.default_machine_id else self.path
        return path.joinpath(name)

    @property
    def _next_num(self):
        files = self.query("[0-9][0-9][0-9][0-9]_.+")
        files.sort(reverse=True)
        if not files:
            return "0001"
        for f in files:
            try:
                return "%04i" % (int(str(f.name).split('_')[0]) + 1)
            except ValueError:
                raise

    def exists(self, bucket, key):
        try:
            return self.client.head_object(Bucket=bucket, Key=key)
        except ClientError:
            return False

    def load_from_s3(self, key):
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read().decode()

    def _create_s3_url(self, key):
        return "s3://%s/%s" % (self.bucket, key)

    def save(self, output_json, save):
        output_file = str(self.get("%s_%s.json" % (self._next_num, save)))
        assert not self.exists(self.bucket, output_file)
        self.client.put_object(
            Bucket=self.bucket,
            Key=output_file,
            Body=safe_dumps(output_json, ensure_ascii=True, indent=4).encode(),
        )
        self.logger.info("Saved benchmark data in: %s" % self._create_s3_url(output_file))

    def query(self, *globs_or_files):
        files = []
        globs = []
        if not globs_or_files:
            globs_or_files = r".+",

        for globish in globs_or_files:
            candidate = urlparse(globish)
            if candidate.scheme == "s3":
                if self.exists(candidate.netloc, candidate.path):
                    files.append(candidate.geturl())
                    continue

            parts = candidate.path.split("/")
            if len(parts) > 2:
                raise ValueError("{0!r} isn't an existing file or acceptable glob. "
                                 "Expected 'platform-glob/filename-glob' or 'filename-glob'.".format(globish))
            elif len(parts) == 2:
                platform_glob, filename_glob = parts
            else:
                platform_glob = self.default_machine_id or r".+"
                filename_glob, = parts or ['']

            filename_glob = filename_glob.rstrip(".+") + r".+\.json"
            globs.append((platform_glob, filename_glob))

        def _list_files(filter):
            paginator = self.client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket, Prefix=str(self.path))
            for page in pages:
                contents = page.get('Contents', [])
                for content in contents:
                    if re.search(filter, content["Key"]):
                        yield Path(content["Key"])

        for platform_glob, filename_glob in globs:
            files.extend(_list_files(os.path.join(platform_glob, filename_glob)))

        return sorted(files, key=lambda file: (file.name, file.parent))

    def load(self, *globs_or_files):
        if not globs_or_files:
            globs_or_files = '[0-9][0-9][0-9][0-9]_',

        for file in self.query(*globs_or_files):
            if file in self._cache:
                data = self._cache[file]
            else:
                try:
                    data = json.loads(self.load_from_s3(str(file)))
                    for bench in data["benchmarks"]:
                        normalize_stats(bench["stats"])
                except Exception as exc:
                    self.logger.warn("Failed to load {0}: {1}".format(file, exc))
                    continue
                self._cache[file] = data
            try:
                relpath = file.relative_to(self.path)
            except ValueError:
                relpath = file
            yield relpath, data

    def load_benchmarks(self, *globs_or_files):
        sources = [
            (short_filename(path), path, data)
            for path, data in self.load(*globs_or_files)
        ]
        common = len(commonpath([src for src, _, _ in sources])) if sources else 0
        for source, path, data in sources:
            source = source[common:].lstrip(r'\/')

            for bench in data["benchmarks"]:
                bench.update(bench.pop("stats"))
                bench['path'] = os.path.join(self.store.geturl(), str(path))
                bench['source'] = source
                yield bench
