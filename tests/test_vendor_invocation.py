"""R-TERMINAL replacement: vendor descendants and input consumption are vendor-owned."""
import os
from pathlib import Path
import signal
import sys
import tempfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bin'))
import _common
from test_stdin_transport import children


def test_c9_complete_means_available_not_consumed(tmp_path):
    result = _common._run_once(
        'claude', [sys.executable, '-c',
                   "import os; os.close(0); print('complete vendor result')"],
        str(tmp_path), 3, stdin_text='input' * 400_000,
    )
    assert result.exit_code == 0
    assert result.stdout.strip() == 'complete vendor result'
    assert result.transport['stdin_delivery'] == 'complete'


def test_c1_captures_stderr_without_live_mirror(tmp_path, capsys):
    result = _common._run_once(
        'claude', [sys.executable, '-c',
                   "import sys; print('PROVIDER_PROGRESS',file=sys.stderr); print('answer')"],
        str(tmp_path), 3,
    )
    assert result.exit_code == 0
    assert result.stderr == 'PROVIDER_PROGRESS\n'
    assert 'PROVIDER_PROGRESS' not in capsys.readouterr().err.splitlines()


def test_c1_display_failure_does_not_replace_result(tmp_path, monkeypatch):
    class BrokenDisplay:
        def write(self, _data):
            raise BrokenPipeError('closed display')
        def flush(self):
            raise BrokenPipeError('closed display')
    monkeypatch.setattr(sys, 'stderr', BrokenDisplay())
    result = _common._run_once(
        'claude', [sys.executable, '-c', "print('answer')"], str(tmp_path), 3,
    )
    assert result.exit_code == 0 and result.stdout == 'answer\n'


def test_c1_large_input_and_both_outputs(tmp_path):
    prompt = '한글😀\r\n' * 100_000
    code = ("import sys; sys.stdout.write('o'*262144); sys.stdout.flush(); "
            "sys.stderr.write('e'*262144); sys.stderr.flush(); "
            "data=sys.stdin.buffer.read(); print(len(data))")
    result = _common._run_once('claude', [sys.executable, '-c', code],
                               str(tmp_path), 5, stdin_text=prompt)
    assert result.exit_code == 0
    assert result.stdout == 'o' * 262144 + str(len(prompt.encode('utf-8'))) + '\n'
    assert result.stderr == 'e' * 262144


def test_capture_snapshot_does_not_follow_growth_or_move_shared_offset():
    with tempfile.TemporaryFile(buffering=0) as stream:
        stream.write(b'first')
        size = os.fstat(stream.fileno()).st_size
        stream.write(b'later')
        assert _common._read_capture(stream, size) == b'first'
        stream.write(b'end')
        assert os.pread(stream.fileno(), 100, 0) == b'firstlaterend'


def test_capture_io_failure_withholds_success(tmp_path, monkeypatch):
    def unavailable(*_args):
        raise OSError('PRIVATE CAPTURE DETAIL')
    monkeypatch.setattr(os, 'pread', unavailable)
    result = _common._run_once('claude', [sys.executable, '-c', "print('answer')"],
                               str(tmp_path), 3)
    assert result.vendor_exit_code == 0
    assert result.exit_code == _common.EXIT_CLI_FAIL
    assert result._output_transport_failed
    assert result.final_answer == '' and result.validated is None
    assert 'PRIVATE' not in result.extraction_error


@pytest.mark.skipif(os.name != 'posix', reason='POSIX termination signals')
def test_timeout_reaps_direct_child_that_ignores_termination(tmp_path, children):
    result = _common._run_once(
        'claude', [sys.executable, '-c',
                   'import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(30)'],
        str(tmp_path), 1,
    )
    assert result.exit_code == _common.EXIT_TIMEOUT
    assert result.vendor_exit_code == -signal.SIGKILL
    assert result.elapsed_s < 9
