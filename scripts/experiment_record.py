"""Turn one measured milestone run into a scoreboard record. Does not launch a browser or a model."""

import argparse
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('experiment_scoreboard', ROOT / 'scripts' / 'experiment_scoreboard.py')
board = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(board)

_PRIVATE_PATH = re.compile(r'(^[/\\])|(^[A-Za-z]:[/\\])|(/Users/)|(/home/)|(/private/)')


def redact(value):
    if isinstance(value, str):
        return '[redacted-path]' if _PRIVATE_PATH.search(value) else value
    if isinstance(value, dict):
        return {key: redact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def build_record(summary, *, arm, hosted_model_calls, evidence_path, lever='measurement', coordinator_tokens=None):
    if summary.get('pilot') is True:
        raise ValueError('A pilot run is not a measured comparison record')
    checks = (summary.get('verification') or {}).get('checks')
    if not isinstance(checks, dict) or not checks or not all(isinstance(value, bool) for value in checks.values()):
        raise ValueError('verification.checks must be a non-empty boolean map')
    goal_id = summary.get('task')
    if not isinstance(goal_id, str) or not goal_id:
        raise ValueError('summary task id is missing')
    latency = summary.get('total_elapsed_ms')
    if isinstance(latency, bool) or not isinstance(latency, (int, float)) or latency <= 0:
        raise ValueError('total_elapsed_ms must be positive')
    steps = summary.get('actions_executed')
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 0:
        raise ValueError('actions_executed must be a non-negative integer')
    record = {'schema': board.SCHEMA, 'arm': arm, 'goal_id': goal_id, 'independent_checks': checks,
              'latency_ms': latency, 'steps': steps, 'hosted_model_calls': hosted_model_calls,
              'done_choice': summary.get('model_done') is True, 'evidence_path': evidence_path, 'lever': lever}
    failure = summary.get('first_observed_failure')
    if isinstance(failure, dict) and isinstance(failure.get('category'), str) and failure['category']:
        record['first_failed_step'] = {'category': failure['category']}
        if isinstance(failure.get('step'), int) and not isinstance(failure.get('step'), bool):
            record['first_failed_step']['step'] = failure['step']
    runtime = summary.get('runtime')
    if isinstance(runtime, dict) and isinstance(runtime.get('peak_worker_bytes'), int):
        record['peak_memory_bytes'] = runtime['peak_worker_bytes']
    calls = summary.get('model_calls_finished')
    if isinstance(calls, int) and not isinstance(calls, bool):
        record['local_model_calls'] = calls
    if coordinator_tokens is not None:
        record['coordinator_tokens'] = coordinator_tokens
    return record


def blocked_record(*, arm, goal_id, reason, hosted_model_calls, evidence_path):
    if not isinstance(reason, str) or not reason:
        raise ValueError('blocked record needs a reason')
    return {'schema': board.SCHEMA, 'arm': arm, 'goal_id': goal_id, 'blocked': True, 'reason': reason,
            'hosted_model_calls': hosted_model_calls, 'evidence_path': evidence_path, 'lever': 'measurement'}


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n')


def write_measured(run_dir, root, arm, hosted_model_calls, lever='measurement', coordinator_tokens=None):
    run_dir = Path(run_dir)
    summary = json.loads((run_dir / 'summary.json').read_text())
    conditions_path = run_dir / 'conditions.json'
    if conditions_path.exists():
        conditions = json.loads(conditions_path.read_text())
        if conditions.get('pilot') is True or summary.get('pilot') is True:
            raise ValueError('A pilot run is not a measured comparison record')
        if conditions.get('task') and summary.get('task') and conditions['task'] != summary['task']:
            raise ValueError('Run task id does not match its conditions')
    else:
        conditions = {}
    goal_id = summary.get('task')
    if not isinstance(goal_id, str) or not goal_id:
        raise ValueError('summary task id is missing')
    folder = Path(root) / 'results' / 'experiment-loop' / arm / goal_id
    evidence_rel = (folder / f'{run_dir.name}.evidence.json').relative_to(root).as_posix()
    record = build_record(summary, arm=arm, hosted_model_calls=hosted_model_calls, evidence_path=evidence_rel,
                          lever=lever, coordinator_tokens=coordinator_tokens)
    evidence = redact({'summary': summary, 'conditions': {key: conditions.get(key) for key in
                       ('task', 'revision', 'source_sha256', 'timeout', 'max_decisions', 'headless')
                       if key in conditions}})
    evidence_path = Path(root) / evidence_rel
    _write_json(evidence_path, evidence)
    try:
        board.judge(record, Path(root))
    except ValueError:
        evidence_path.unlink(missing_ok=True)
        raise
    record_path = folder / f'{run_dir.name}.json'
    _write_json(record_path, record)
    return record_path


def write_blocked(root, arm, goal_id, reason, hosted_model_calls):
    folder = Path(root) / 'results' / 'experiment-loop' / arm / goal_id
    evidence_rel = (folder / 'blocked.evidence.json').relative_to(root).as_posix()
    _write_json(Path(root) / evidence_rel, {'reason': reason})
    record = blocked_record(arm=arm, goal_id=goal_id, reason=reason, hosted_model_calls=hosted_model_calls,
                            evidence_path=evidence_rel)
    try:
        board.judge(record, Path(root))
    except ValueError:
        (Path(root) / evidence_rel).unlink(missing_ok=True)
        raise
    record_path = folder / 'blocked.json'
    _write_json(record_path, record)
    return record_path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--arm', required=True, choices=board.ARMS)
    parser.add_argument('--hosted-model-calls', type=int, required=True)
    parser.add_argument('--run-dir', type=Path)
    parser.add_argument('--blocked', action='store_true')
    parser.add_argument('--reason')
    parser.add_argument('--goal', default=board.PRIMARY)
    parser.add_argument('--lever', default='measurement')
    args = parser.parse_args(argv)
    if args.blocked == bool(args.run_dir):
        parser.error('Pass either --run-dir or --blocked')
    if args.blocked:
        path = write_blocked(args.root, args.arm, args.goal, args.reason, args.hosted_model_calls)
    else:
        path = write_measured(args.run_dir, args.root, args.arm, args.hosted_model_calls, lever=args.lever)
    print(path.relative_to(args.root).as_posix())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
