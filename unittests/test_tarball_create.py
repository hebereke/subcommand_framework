import os
import tarfile

from utils import tarball_create, TARBALL_TIMESTAMP_FILE


def make_sample_dir(path, name="pkg"):
    d = path / name
    d.mkdir()
    f = d / 'a.txt'
    f.write_text('hello')
    return str(d)


def test_tarball_create_basic(tmp_path):
    target = make_sample_dir(tmp_path, 'pkg')
    out = tarball_create(target, dstdir=str(tmp_path))
    assert os.path.isabs(out)
    assert os.path.isfile(out)
    with tarfile.open(out, 'r:gz') as t:
        names = t.getnames()
        assert 'pkg' in names
        assert 'pkg/a.txt' in names
        # timestamp file should be included inside the tarball
        assert f'pkg/{TARBALL_TIMESTAMP_FILE}' in names


def test_tarball_create_delete_target(tmp_path):
    target = make_sample_dir(tmp_path, 'remove_me')
    out = tarball_create(target, dstdir=str(tmp_path), delete_target=True)
    assert os.path.isfile(out)
    assert not os.path.exists(target)


def test_tarball_create_invalid_dstdir_raises(tmp_path):
    target = make_sample_dir(tmp_path, 'pkg2')
    bad_dstdir = tmp_path / 'no_such_dir'
    try:
        tarball_create(target, dstdir=str(bad_dstdir))
        raised = False
    except FileNotFoundError:
        raised = True
    assert raised


def test_tarball_create_invalid_tarout_extension_raises(tmp_path):
    target = make_sample_dir(tmp_path, 'pkg3')
    bad_tarout = tmp_path / 'out.tar'
    try:
        tarball_create(target, tarout=str(bad_tarout))
        raised = False
    except ValueError:
        raised = True
    assert raised
