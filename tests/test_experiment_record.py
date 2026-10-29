"""The measured-run recorder copies verifier checks and drops private paths."""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('experiment_record', ROOT / 'scripts' / 'experiment_record.py')
recorder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(recorder)


def summary(**overrides):
    body = {'task': 'local_search', 'pilot': False, 'total_elapsed_ms': 1500, 'actions_executed': 3,
            'model_done': True, 'outcome_verified': True,
            'verification': {'passed': False, 'checks': {'origin': False, 'results_visible': False,
                                                         'no_flight_selected': True}},
            'first_observed_failure': {'category': 'premature_completion', 'step': 4,
                                       'cause': 'saved under /Users/example/trace'},
            'runtime': {'peak_worker_bytes': 42}, 'peak_mlx_bytes': 99, 'model_calls_finished': 2}
    body.update(overrides)
    return body


def write_run(tmp_path, payload, pilot=False):
    run = tmp_path / 'artifacts' / 'milestone' / 'local_search-1'
    run.mkdir(parents=True, exist_ok=True)
    (run / 'summary.json').write_text(json.dumps(payload))
    (run / 'conditions.json').write_text(json.dumps({'task': 'local_search', 'pilot': pilot, 'revision': 'abc'}))
    return run


def test_done_and_outcome_flag_do_not_override_failed_checks(tmp_path):
    path = recorder.write_measured(write_run(tmp_path, summary()), tmp_path, 'local-coordinator', 0)
    record = json.loads(path.read_text())
    assert record['done_choice'] is True
    assert record['independent_checks']['origin'] is False
    judged = recorder.board.judge(record, tmp_path)
    assert judged['passed'] is False
    evidence = json.loads((tmp_path / record['evidence_path']).read_text())
    assert evidence['summary']['first_observed_failure']['cause'] == '[redacted-path]'
    assert 'peak_memory_bytes' in record and record['peak_memory_bytes'] == 42
    assert 'peak_mlx_bytes' not in record


def test_missing_checks_and_pilot_runs_write_nothing(tmp_path):
    bare = summary()
    bare.pop('verification')
    with pytest.raises(ValueError, match='verification.checks'):
        recorder.write_measured(write_run(tmp_path, bare), tmp_path, 'local-coordinator', 0)
    with pytest.raises(ValueError, match='pilot'):
        recorder.write_measured(write_run(tmp_path, summary(), pilot=True), tmp_path, 'local-coordinator', 0)
    assert not (tmp_path / 'results').exists()


def test_blocked_arm_records_a_reason_without_a_pass(tmp_path):
    path = recorder.write_blocked(tmp_path, 'grok-4.7', 'local_search', 'Grok CLI is not logged in', 0)
    record = json.loads(path.read_text())
    judged = recorder.board.judge(record, tmp_path)
    assert judged['blocked'] is True
    assert judged['passed'] is False
    summary = recorder.board.summarize([record], tmp_path)
    assert summary['speedups']['local_search']['grok-4.7']['comparable'] is False
