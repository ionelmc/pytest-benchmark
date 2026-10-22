import json
from unittest.mock import Mock

import pytest

from pytest_benchmark.storage.file import FileStorage


@pytest.mark.parametrize('machine', [None, 'machine'])
@pytest.mark.parametrize('previous', [9998, 9999, 10000, 10001, 99999])
def test_save_and_load_after_four_digit_sequence(tmp_path, machine, previous):
    storage = FileStorage(tmp_path, Mock(), default_machine_id=machine)
    directory = tmp_path / machine if machine else tmp_path
    directory.mkdir(exist_ok=True)
    data = {'benchmarks': []}
    old_file = directory / f'{previous:04}_example.json'
    old_file.write_text(json.dumps(data), encoding='utf8')

    storage.save(data, 'example')

    new_file = directory / f'{previous + 1:04}_example.json'
    assert new_file.exists()
    assert old_file.read_text(encoding='utf8') == json.dumps(data)
    assert {path.name for path, _ in storage.load()} == {old_file.name, new_file.name}


@pytest.mark.parametrize('prefix', ['0001extra', '0001²'])
def test_sequence_ignores_nonnumeric_prefixes(tmp_path, prefix):
    (tmp_path / f'{prefix}_example.json').touch()
    assert FileStorage(tmp_path, Mock())._next_num == '0001'


def test_sequence_uses_numeric_maximum(tmp_path):
    for prefix in ['9999', '10000', '10001']:
        (tmp_path / f'{prefix}_example.json').touch()
    assert FileStorage(tmp_path, Mock())._next_num == '10002'
