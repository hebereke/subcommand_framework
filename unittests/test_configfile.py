import pytest
from dataclasses import dataclass
from pathlib import Path, PosixPath

from configfile import initialize_params

@dataclass
class SampleConfig:
    a: int = 0
    b: float = 0.0
    c: str = ''
    d: list = field(default_factory=list)
    e: bool = False
    p: PosixPath = Path('/')

from dataclasses import field

def test_initialize_params_conversion(tmp_path):
    params = {
        'a': '3',
        'b': '1.5',
        'c': 123,
        'd': [1,2,3],
        'e': 'True',
        'p': str(tmp_path)
    }
    out = initialize_params(SampleConfig, params)
    assert isinstance(out['a'], int)
    assert out['a'] == 3
    assert isinstance(out['b'], float)
    assert out['b'] == pytest.approx(1.5)
    assert isinstance(out['c'], str)
    assert out['c'] == '123'
    assert isinstance(out['d'], list)
    assert out['d'] == [1,2,3]
    assert isinstance(out['e'], bool)
    assert out['e'] is True
    assert isinstance(out['p'], Path)
    assert str(out['p']) == str(tmp_path)
