import json
from unittest.mock import Mock

import pytest

from pytest_benchmark.stats import Stats
from pytest_benchmark.storage.file import FileStorage


@pytest.mark.parametrize('machine', ['', 'machine'])
@pytest.mark.parametrize('names', [('0001_example',), ('0001_example', '0002_example')])
def test_source_labels_keep_filenames(tmp_path, machine, names):
    stats = Stats()
    stats.update(1.0)
    directory = tmp_path / machine
    directory.mkdir(exist_ok=True)
    for name in names:
        data = {'benchmarks': [{'name': 'example', 'stats': stats.as_dict()}]}
        (directory / f'{name}.json').write_text(json.dumps(data), encoding='utf8')
    storage = FileStorage(tmp_path, Mock())

    assert [bench['source'] for bench in storage.load_benchmarks()] == list(names)
