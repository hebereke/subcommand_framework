import os
import stat

from utils import chmod, recursive_chmod

def test_chmod_add_exec(tmp_path):
    p = tmp_path / 'f'
    p.write_text('x')
    os.chmod(p, 0o600)
    chmod(str(p), 'u+rx')
    st = os.stat(p)
    assert bool(st.st_mode & stat.S_IXUSR)
    assert bool(st.st_mode & stat.S_IRUSR)

def test_recursive_chmod(tmp_path):
    d = tmp_path / 'd'
    d.mkdir()
    f = d / 'file'
    f.write_text('x')
    os.chmod(f, 0o600)
    recursive_chmod(str(d), 'u+rx')
    st = os.stat(f)
    assert bool(st.st_mode & stat.S_IXUSR)
    assert bool(st.st_mode & stat.S_IRUSR)
