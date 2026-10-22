import json
from copy import deepcopy
from unittest.mock import Mock

from pytest_benchmark.stats import Stats
from pytest_benchmark.storage.file import FileStorage


def test_loading_benchmarks_does_not_mutate_cached_results(tmp_path):
    stats = Stats()
    stats.update(1.0)
    data = {'benchmarks': [{'name': 'example', 'stats': stats.as_dict()}]}
    (tmp_path / '0001_example.json').write_text(json.dumps(data), encoding='utf8')
    storage = FileStorage(tmp_path, Mock())
    original = deepcopy(list(storage.load()))

    first = deepcopy(list(storage.load_benchmarks()))
    second = list(storage.load_benchmarks())

    assert second == first
    assert list(storage.load()) == original
    assert 'stats' not in first[0]
    assert first[0]['mean'] == 1.0
