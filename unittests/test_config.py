import pytest
from dataclasses import dataclass, field
from config import GlobalConfig, config


def teardown_function(function):
    # ensure global config cleared between tests
    GlobalConfig.reset()


def test_set_config_requires_dataclass():
    with pytest.raises(TypeError):
        GlobalConfig.set_config({'not': 'dataclass'})


def test_set_get_and_reset():
    @dataclass
    class Sample:
        a: int = 1
        b: str = 'x'

    # set config
    GlobalConfig.set_config(Sample())
    assert GlobalConfig.is_valid()
    assert GlobalConfig.get('a') == 1

    # set value via GlobalConfig.set
    GlobalConfig.set('a', 5)
    assert GlobalConfig.get('a') == 5

    # proxy access
    assert config.a == 5

    # keys/values/items
    keys = GlobalConfig.keys()
    assert 'a' in keys and 'b' in keys
    vals = GlobalConfig.values()
    assert isinstance(vals, tuple)
    items = GlobalConfig.items()
    assert any(k == 'a' and v == 5 for k, v in items)

    # reset
    GlobalConfig.reset()
    assert GlobalConfig.is_empty()


def test_extend_schema_merges_fields():
    @dataclass
    class Base:
        x: int = 1

    @dataclass
    class Extra:
        y: str = 'z'

    GlobalConfig.set_config(Base())
    # extend schema
    GlobalConfig.extend_schema(Extra)
    # after extend, proxy should expose new field
    assert 'y' in GlobalConfig.keys()
    # new instance retains previous values
    assert GlobalConfig.get('x') == 1
    # set new field
    GlobalConfig.set('y', 'hello')
    assert GlobalConfig.get('y') == 'hello'
