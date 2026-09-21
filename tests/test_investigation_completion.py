"""C15/C25/C28/C29 public wrapper boundaries, with synthetic providers only."""
import contextlib
import hashlib
import json
from pathlib import Path
import sys

import pytest

SOURCE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(SOURCE / 'bin'), str(SOURCE / 'tests')]
import _common
import antigravity_wrapper as agy
import claude_wrapper as claude
import gemini_wrapper as gemini
from test_wrapper_relative_paths import paths, fake_provider, WRAPPERS


@pytest.mark.parametrize('wrapper', WRAPPERS)
@pytest.mark.parametrize('redacted', [False, True])
def test_c28_success_paths_are_resolved_and_use_existing_audit_masking(
    wrapper, redacted, paths, fake_provider, monkeypatch, capsys,
):
    caller, child = paths
    captured = []
    monkeypatch.setenv('TRIAD_AUDIT_REDACT_PROMPTS', '1' if redacted else '0')
    monkeypatch.delenv('TRIAD_WRAPPER_HARDENED', raising=False)
    monkeypatch.setattr(_common, '_LOG_DIR', caller / 'logs')
    monkeypatch.setattr(_common, '_LOG_DIR_CONFIGURED', True)
    def persist(cli, wrapper_cmd, cmd, prompt, result, **kwargs):
        captured.append(result)
        assert _common.audit(cli, cmd, prompt, result)
    target = _common if wrapper is agy else wrapper
    monkeypatch.setattr(target, 'persist_result_artifacts', persist)
    monkeypatch.setattr(sys, 'argv', [wrapper.__file__, '--prompt-file', 'prompt.txt', '--cwd', 'child'])
    assert wrapper.main() == 0
    records = list((caller / 'logs').glob('*/audit.jsonl'))
    assert len(records) == 1
    record = json.loads(records[0].read_text())
    assert record['resolved_prompt_file'] == ('<redacted:prompt-file-path>' if redacted else str(caller / 'prompt.txt'))
    assert record['effective_cwd'] == ('<redacted:cwd-path>' if redacted else str(child))
    summary = capsys.readouterr().err
    assert 'resolved_prompt_file=' in summary and 'effective_cwd=' in summary
    assert str(caller) not in summary if redacted else str(caller / 'prompt.txt') in summary


@pytest.mark.parametrize('wrapper', WRAPPERS)
@pytest.mark.parametrize('redacted', [False, True])
def test_c28_refusal_identifies_candidate_without_disclosing_masked_path(
    wrapper, redacted, paths, fake_provider, monkeypatch, capsys,
):
    caller, _ = paths
    monkeypatch.setenv('TRIAD_AUDIT_REDACT_PROMPTS', '1' if redacted else '0')
    monkeypatch.setattr(sys, 'argv', [wrapper.__file__, '--prompt-file', 'missing.txt'])
    assert wrapper.main() == _common.EXIT_ARG_ERROR
    error = capsys.readouterr().err
    assert str(caller) not in error if redacted else str(caller / 'missing.txt') in error
    assert fake_provider == ([], [])


@pytest.mark.parametrize('wrapper', WRAPPERS)
def test_c25_authorized_extra_roots_reach_native_raw_option(
    wrapper, paths, fake_provider, monkeypatch,
):
    caller, child = paths
    extra = caller / 'library 한글'
    extra.mkdir()
    captured = []
    if wrapper is agy:
        prior = agy._build_cmd
        def build(*args, **kwargs):
            command = prior(*args, **kwargs)
            captured.append(command)
            return command
        monkeypatch.setattr(agy, '_build_cmd', build)
    else:
        def run(cli, build, prompt, **kwargs):
            captured.append(build(prompt))
            return _common.RunResult(exit_code=0, stdout='', stderr='', elapsed_s=0,
                classification='ok', final_answer='raw answer')
        monkeypatch.setattr(wrapper, 'run_cli_with_retry', run)
    monkeypatch.setattr(sys, 'argv', [wrapper.__file__, '--prompt-file', 'prompt.txt',
        '--cwd', 'child', '--add-dir', 'library 한글'])
    assert wrapper.main() == 0
    flag = '--include-directories' if wrapper is gemini else '--add-dir'
    assert captured[0][captured[0].index(flag) + 1] == str(extra)


@pytest.mark.parametrize('wrapper', WRAPPERS)
def test_c25_invalid_extra_root_refuses_before_provider(wrapper, paths, fake_provider, monkeypatch):
    monkeypatch.setattr(sys, 'argv', [wrapper.__file__, '--prompt', 'inspect', '--add-dir', 'missing'])
    assert wrapper.main() == _common.EXIT_ARG_ERROR
    assert fake_provider == ([], [])


@pytest.mark.parametrize('web', [False, True])
def test_c29_gemini_explicit_web_trigger_keeps_caller_and_substitutes_tools_last(
    web, paths, fake_provider, monkeypatch,
):
    captured = []
    caller = "Research actual API; literal $(x) ' \\ 한글\n "
    def run(cli, build, prompt, **kwargs):
        sent = prompt + ('\n\n' + kwargs['prompt_suffix'] if kwargs.get('prompt_suffix') else '')
        captured.append((sent, build(sent)))
        return _common.RunResult(exit_code=0, stdout='', stderr='', elapsed_s=0,
            classification='ok', final_answer='answer')
    monkeypatch.setattr(gemini, 'run_cli_with_retry', run)
    monkeypatch.setattr(sys, 'argv', [gemini.__file__, '--prompt', caller, *(['--web'] if web else [])])
    assert gemini.main() == 0
    clause = agy._load_web_evidence_clause().replace('search_web', 'google_web_search').replace('read_url_content', 'web_fetch')
    assert captured[0][0] == caller + '\n\n' + clause if web else captured[0][0] == caller
    assert '--web' not in captured[0][1]


def test_c15_b_profile_is_exact_candidate_and_denies_web():
    path = SOURCE / 'bin/policies/gemini-formal-readonly.toml'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == '01a267f591518964e30f94ffc45d496aae594435678380179b679d1aa8de189b'
    assert not {'google_web_search', 'web_fetch'} & gemini.FORMAL_READ_TOOLS
    assert {'google_web_search', 'web_fetch'} <= gemini.FORMAL_DENIED_TOOLS
    assert gemini._validate_formal_policy(path)


def test_c15_policy_comment_change_cannot_bypass_exact_candidate_bytes(tmp_path):
    policy = tmp_path / 'gemini-formal-readonly.toml'
    policy.write_bytes(gemini._formal_policy_path().read_bytes() + b'\n# changed\n')
    (tmp_path / 'source-manifest.json').write_bytes((gemini._formal_policy_path().parent / 'source-manifest.json').read_bytes())
    with pytest.raises(ValueError, match='digest'):
        gemini._validate_formal_policy(policy)


@pytest.mark.parametrize('wrapper', WRAPPERS)
def test_c25_extra_roots_cannot_expand_a_formal_invocation(wrapper, paths, fake_provider, monkeypatch):
    monkeypatch.setattr(sys, 'argv', [wrapper.__file__, '--prompt', 'review',
        '--add-dir', 'child', '--expected-review-id', 'r1'])
    assert wrapper.main() == _common.EXIT_ARG_ERROR
    assert fake_provider == ([], [])


@pytest.mark.parametrize('extra', [
    ['--expected-review-id', 'r1'], ['--preflight-only'],
    ['--pydantic', 'verdict_schema:LegVerdict'],
])
def test_c29_web_cannot_enter_gemini_review(paths, fake_provider, monkeypatch, extra):
    monkeypatch.setattr(sys, 'argv', [gemini.__file__, '--prompt', 'review', '--web', *extra])
    assert gemini.main() == _common.EXIT_ARG_ERROR
    assert fake_provider == ([], [])


@pytest.mark.parametrize('repair', [False, True])
def test_c29_gemini_custom_schema_keeps_web_clause_last_through_native_call(
    repair, paths, fake_provider, monkeypatch, capsys,
):
    commands = []
    def once(cli, cmd, cwd, timeout, **kwargs):
        commands.append(cmd)
        answer = {} if repair and len(commands) == 1 else {'ok': True}
        return _common.RunResult(exit_code=0, vendor_exit_code=0,
            stdout=json.dumps({'response': json.dumps(answer)}), stderr='',
            elapsed_s=0, classification='ok')
    monkeypatch.setattr(_common, '_run_once', once)
    monkeypatch.setattr(gemini, 'run_cli_with_retry', _common.run_cli_with_retry)
    monkeypatch.setattr(sys, 'argv', [gemini.__file__, '--prompt', 'Research primary API',
        '--web', '--pydantic', 'test_antigravity_stream_json:_Answer', '--model', 'selected-model'])
    assert gemini.main() == 0
    assert len(commands) == (2 if repair else 1)
    clause = agy._load_web_evidence_clause().replace('search_web', 'google_web_search').replace('read_url_content', 'web_fetch')
    for command in commands:
        sent = command[command.index('-p') + 1]
        assert 'Research primary API' in sent
        assert sent.endswith(clause) and sent.count(clause) == 1
    assert commands[0][commands[0].index('-m') + 1] == 'selected-model'
    assert json.loads(capsys.readouterr().out) == {'ok': True}


def test_c29_missing_gemini_clause_refuses_without_provider(
    paths, fake_provider, monkeypatch, capsys,
):
    def missing(*args, **kwargs):
        raise ValueError('missing canonical clause')
    monkeypatch.setattr(_common, 'load_web_evidence_clause', missing)
    monkeypatch.setattr(sys, 'argv', [gemini.__file__, '--prompt', 'research', '--web'])
    assert gemini.main() == _common.EXIT_ARG_ERROR
    assert fake_provider == ([], [])
    assert 'missing canonical clause' in capsys.readouterr().err


def test_c28_real_exec_summary_masks_cwd_and_extra_input_argv(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv('TRIAD_AUDIT_REDACT_PROMPTS', '1')
    result = _common._run_once('claude', [sys.executable, '-c', 'print("ok")'], str(tmp_path), 5)
    assert result.exit_code == 0
    summary = capsys.readouterr().err
    assert str(tmp_path) not in summary and '<redacted:cwd-path>' in summary
    redacted = _common._redact_prompt_args(['cli', '--add-dir', str(tmp_path), '--include-directories', str(tmp_path)])
    assert str(tmp_path) not in redacted


def test_c25_gemini_refuses_comma_directory_without_splitting_permissions(paths, fake_provider, monkeypatch):
    caller, _ = paths
    (caller / 'a,b').mkdir()
    monkeypatch.setattr(sys, 'argv', [gemini.__file__, '--prompt', 'inspect', '--add-dir', 'a,b'])
    assert gemini.main() == _common.EXIT_ARG_ERROR
    assert fake_provider == ([], [])


@pytest.mark.parametrize('wrapper', WRAPPERS)
def test_c28_unavailable_entry_cwd_remains_argument_error(wrapper, paths, fake_provider, monkeypatch):
    def unavailable(cls):
        raise FileNotFoundError('entry cwd disappeared')
    monkeypatch.setattr(sys, 'argv', [wrapper.__file__, '--prompt', 'inspect'])
    monkeypatch.setattr(Path, 'cwd', classmethod(unavailable))
    assert wrapper.main() == _common.EXIT_ARG_ERROR
    assert fake_provider == ([], [])
