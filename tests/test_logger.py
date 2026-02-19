import tempfile
from logger import get_logger

def test_logger_result_writes_file(tmp_path):
    logfile = tmp_path / 'out.log'
    logger = get_logger('testlogger')
    logger.result('hello world', logfile=str(logfile), output_stdout=False)
    assert logfile.exists()
    with open(logfile, 'r', encoding='utf-8') as f:
        data = f.read()
    assert 'hello world' in data
