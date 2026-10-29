"""Safeguards for the fixed-goal scoreboard. No browser and no model calls."""

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('experiment_scoreboard', ROOT / 'scripts' / 'experiment_scoreboard.py')
board = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(board)


def record(root, name, **overrides):
    evidence = Path('results') / f'{name}.json'
    (root / evidence).parent.mkdir(parents=True, exist_ok=True)
    (root / evidence).write_text('{}\n')
    body = {'schema': board.SCHEMA, 'arm': 'local-coordinator', 'goal_id': 'local_search',
            'independent_checks': {'origin': True, 'results_visible': True}, 'latency_ms': 1000, 'steps': 4,
            'hosted_model_calls': 0, 'done_choice': True, 'evidence_path': evidence.as_posix()}
    body.update(overrides)
    return body


def test_done_choice_does_not_decide_the_outcome(tmp_path):
    failed = record(tmp_path, 'done-fail', independent_checks={'origin': False})
    judged = board.judge(failed, tmp_path)
    assert judged['done_choice'] is True
    assert judged['passed'] is False
    passed = board.judge(record(tmp_path, 'checks-pass', done_choice=False), tmp_path)
    assert passed['passed'] is True


def test_missing_or_escaping_evidence_rejects_the_record(tmp_path):
    body = record(tmp_path, 'gone')
    (tmp_path / body['evidence_path']).unlink()
    with pytest.raises(ValueError, match='evidence file missing'):
        board.judge(body, tmp_path)
    escaped = record(tmp_path, 'escape', evidence_path='../outside.json')
    with pytest.raises(ValueError, match='inside the repository'):
        board.judge(escaped, tmp_path)


def test_hypothesis_arm_rejects_hosted_calls_and_grok_pass_requires_one(tmp_path):
    with pytest.raises(ValueError, match='hosted model call'):
        board.judge(record(tmp_path, 'hosted', hosted_model_calls=1), tmp_path)
    grok = record(tmp_path, 'grok', arm='grok-4.7', hosted_model_calls=0)
    with pytest.raises(ValueError, match='hosted call'):
        board.judge(grok, tmp_path)
    blocked = record(tmp_path, 'blocked', arm='grok-4.7', hosted_model_calls=0, blocked=True,
                     reason='Grok CLI is not logged in', independent_checks={})
    assert board.judge(blocked, tmp_path)['blocked'] is True


def test_inconsistent_tokens_and_non_boolean_checks_are_rejected(tmp_path):
    tokens = {'input': 3, 'output': 1, 'total': 5}
    with pytest.raises(ValueError, match='inconsistent'):
        board.judge(record(tmp_path, 'tokens', coordinator_tokens=tokens), tmp_path)
    with pytest.raises(ValueError, match='boolean'):
        board.judge(record(tmp_path, 'text-check', independent_checks={'origin': 'true'}), tmp_path)


def test_failed_fast_run_does_not_count_as_a_speedup(tmp_path):
    runs = [
        record(tmp_path, 'local-fail', latency_ms=10, independent_checks={'origin': False},
               first_failed_step={'category': 'wrong_decision'}),
        record(tmp_path, 'browser', arm='browser-use', latency_ms=5000, hosted_model_calls=2),
    ]
    summary = board.summarize(runs, tmp_path)
    item = summary['speedups']['local_search']['browser-use']
    assert item['comparable'] is False
    assert item['latency'] is None
    assert board.combined_score(summary) is None
    assert item['baseline_evidence'] == ['results/browser.json']
    assert summary['hypothesis_alive'] is True


def test_passing_runs_report_speedup_with_evidence_paths(tmp_path):
    tokens = {'input': 80, 'cached_input': 50, 'output': 20, 'total': 100}
    runs = [
        record(tmp_path, 'local', latency_ms=1000, steps=4, coordinator_tokens={'input': 10, 'output': 0, 'total': 10},
               peak_memory_bytes=100),
        record(tmp_path, 'browser', arm='browser-use', latency_ms=4000, steps=8, hosted_model_calls=3,
               coordinator_tokens=tokens, peak_memory_bytes=50),
        record(tmp_path, 'grok', arm='grok-4.7', latency_ms=2000, steps=6, hosted_model_calls=1),
        record(tmp_path, 'delegated', arm='grok-4.7+zero-browser', blocked=True, reason='not run',
               hosted_model_calls=0),
    ]
    summary = board.summarize(runs, tmp_path)
    browser = summary['speedups']['local_search']['browser-use']
    assert browser['latency'] == 4
    assert browser['steps'] == 2
    assert browser['tokens'] == 10
    assert browser['hypothesis_evidence'] == ['results/local.json']
    assert summary['arms']['local-coordinator:local_search']['peak_memory_bytes_max'] == 100
    assert summary['next_lever']['action'] == 'repeat-goal'


def test_evidence_sidecar_does_not_block_scoring(tmp_path):
    runs = tmp_path / 'results' / 'experiment-loop'
    runs.mkdir(parents=True)
    body = record(tmp_path, 'local')
    (runs / 'local.json').write_text(json.dumps(body))
    (runs / 'local.evidence.json').write_text('{"note": "sidecar"}\n')
    summary = board.summarize(board.load_records(runs), tmp_path)
    assert summary['arms']['local-coordinator:local_search']['passes'] == 1


def test_premature_done_selects_the_prompt_lever():
    rows = [{'arm': 'local-coordinator', 'goal_id': 'local_search', 'passed': False, 'blocked': False,
             'category': 'premature_completion', 'lever': 'measurement', 'evidence_path': 'results/local.json'}]
    for arm in board.BASELINES:
        rows.append({'arm': arm, 'goal_id': 'local_search', 'passed': False, 'blocked': True, 'category': None,
                     'lever': 'measurement', 'evidence_path': f'results/{arm}.json'})
    choice = board.recommend(rows, {'local_search': {}})
    assert choice['lever'] == 'prompt'
    assert choice['hypothesis_alive'] is True


def test_three_failures_after_the_matching_lever_stop_the_line():
    rows = [{'arm': 'local-coordinator', 'goal_id': 'local_search', 'passed': False, 'blocked': False,
             'category': 'wrong_decision', 'lever': 'prompt', 'evidence_path': f'results/{index}.json'}
            for index in range(3)]
    for arm in board.BASELINES:
        rows.append({'arm': arm, 'goal_id': 'local_search', 'passed': True, 'blocked': False, 'category': None,
                     'lever': 'measurement', 'evidence_path': f'results/{arm}.json', 'latency_ms': 10, 'steps': 1,
                     'tokens': None})
    choice = board.recommend(rows, {'local_search': {}})
    assert choice['action'] == 'stop'
    assert choice['hypothesis_alive'] is False


def test_slower_passing_runs_try_caching_once_then_stop():
    local = [{'arm': 'local-coordinator', 'goal_id': 'local_search', 'passed': True, 'blocked': False,
              'category': None, 'lever': 'measurement', 'latency_ms': 100, 'steps': 2, 'tokens': None,
              'evidence_path': f'results/local-{index}.json'} for index in range(3)]
    baselines = []
    for arm in board.BASELINES:
        baselines.append({'arm': arm, 'goal_id': 'local_search', 'passed': True, 'blocked': False,
                          'category': None, 'lever': 'measurement', 'latency_ms': 40, 'steps': 2, 'tokens': None,
                          'evidence_path': f'results/{arm}.json'})
    speedups = board.speedups_for(local + baselines)
    assert board.recommend(local + baselines, speedups)['lever'] == 'caching'
    cached = [dict(row, lever='caching') for row in local]
    assert board.recommend(cached + baselines, board.speedups_for(cached + baselines))['action'] == 'stop'


def test_mlflow_logs_measured_ratios_only(tmp_path, monkeypatch):
    calls = {}

    class Run:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    fake = SimpleNamespace(
        set_tracking_uri=lambda uri: calls.setdefault('uri', uri),
        get_experiment_by_name=lambda name: object(),
        set_experiment=lambda name: calls.setdefault('experiment', name),
        start_run=lambda **kwargs: Run(),
        log_metric=lambda key, value: calls.setdefault('metrics', {}).setdefault(key, value),
        log_artifact=lambda path: calls.setdefault('artifact', path))
    monkeypatch.setitem(sys.modules, 'mlflow', fake)
    summary = board.summarize([
        record(tmp_path, 'local', latency_ms=1000),
        record(tmp_path, 'browser', arm='browser-use', latency_ms=3000, hosted_model_calls=1),
    ], tmp_path)
    artifact = tmp_path / 'summary.json'
    artifact.write_text(json.dumps(summary))
    assert board.log_mlflow(summary, tmp_path / 'mlflow', artifact)['logged'] is True
    assert calls['experiment'] == 'zero-browser-local-coordinator'
    assert 'local_search.browser-use.latency' in calls['metrics']
    assert calls['metrics']['local_search.browser-use.latency'] == 3
    assert all(value is not None for value in calls['metrics'].values())


def test_empty_run_directory_does_not_write_numbers(tmp_path):
    assert board.main(['--runs', str(tmp_path / 'missing'), '--output', str(tmp_path / 'out.json')]) == 2
    assert not (tmp_path / 'out.json').exists()


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_proposal_and_tracking_wait_for_real_records(tmp_path):
    propose = _load('experiment_propose', ROOT / 'scripts' / 'experiment_propose.py')
    track = _load('experiment_track', ROOT / 'scripts' / 'experiment_track.py')
    output = tmp_path / 'proposed-idea.json'
    assert propose.main(['--runs', str(tmp_path / 'missing'), '--output', str(output)]) == 2
    assert not output.exists()
    assert track.main(['--runs', str(tmp_path / 'missing'), '--output', str(tmp_path / 'summary.json')]) == 2
    assert not (tmp_path / 'summary.json').exists()
    assert not (tmp_path / 'mlflow').exists()


def test_proposal_uses_the_recorded_lever_and_skips_unmeasured_ratios(tmp_path):
    runs = tmp_path / 'results' / 'experiment-loop'
    runs.mkdir(parents=True)
    body = record(tmp_path, 'local', independent_checks={'origin': False},
                  first_failed_step={'category': 'wrong_decision'})
    (runs / 'local.json').write_text(json.dumps(body))
    summary = board.summarize(board.load_records(runs), tmp_path)
    rubrics = json.loads((ROOT / 'experiments' / 'local-coordinator' / 'rubrics.json').read_text())
    idea = board.propose_idea(summary, rubrics)
    assert idea['next_lever'] == summary['next_lever']
    assert idea['hypothesis'] == summary['next_lever']['reason']
    assert 'measured_latency_ratios' not in idea
    assert idea['evidence_paths'] == ['results/local.json']
    assert idea['source'] == 'SakanaAI/AI-Scientist-v3 idea schema'


def test_evaluator_does_not_invent_a_zero_score(tmp_path):
    evaluate = _load('evaluate', ROOT / 'experiments' / 'local-coordinator' / 'evaluate.py')
    assert evaluate.main(tmp_path / 'missing', tmp_path / 'out', tmp_path) == 1
    metrics = json.loads((tmp_path / 'out' / 'metrics.json').read_text())
    assert metrics['combined_score'] is None


def test_mlflow_file_store_keeps_only_measured_metrics(tmp_path):
    pytest.importorskip('mlflow')
    runs = tmp_path / 'results' / 'experiment-loop'
    runs.mkdir(parents=True)
    local = record(tmp_path, 'local', latency_ms=1000)
    browser = record(tmp_path, 'browser', arm='browser-use', latency_ms=3000, hosted_model_calls=1)
    (runs / 'local.json').write_text(json.dumps(local))
    (runs / 'browser.json').write_text(json.dumps(browser))
    summary = board.summarize(board.load_records(runs), tmp_path)
    artifact = tmp_path / 'summary.json'
    artifact.write_text(json.dumps(summary))
    uri = tmp_path / 'mlflow'
    logged = board.log_mlflow(summary, uri, artifact)
    assert logged['logged'] is True
    from mlflow.tracking import MlflowClient
    client = MlflowClient(tracking_uri=logged['tracking_uri'])
    experiment = client.get_experiment_by_name('zero-browser-local-coordinator')
    found = client.search_runs([experiment.experiment_id])
    assert len(found) == 1
    metrics = found[0].data.metrics
    assert metrics['local_search.browser-use.latency'] == 3
    assert all(value is not None for value in metrics.values())
    assert not any(key.startswith('local_search.grok') for key in metrics)
