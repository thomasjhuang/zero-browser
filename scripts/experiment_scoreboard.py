"""Score fixed-goal browser runs from evidence files. A DONE choice is not success."""

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 'zero-browser.experiment-run.v1'
HYPOTHESIS = 'local-coordinator'
BASELINES = ('browser-use', 'grok-4.7', 'grok-4.7+zero-browser')
ARMS = (HYPOTHESIS,) + BASELINES
GROK_ARMS = {'grok-4.7', 'grok-4.7+zero-browser'}
PRIMARY = 'local_search'
VARIATION = 'local_search_reordered'
LEVER_FOR_CATEGORY = {'wrong_decision': 'prompt', 'incorrect_field_text': 'field-text'}


def evidence_file(root, record):
    raw = record.get('evidence_path')
    if not isinstance(raw, str) or not raw or raw.startswith(('/', '\\')) or ':' in raw[:3]:
        raise ValueError('evidence_path must be a relative repository path')
    parts = Path(raw).parts
    if '..' in parts or any('\\' in part for part in parts):
        raise ValueError('evidence_path must stay inside the repository')
    path = (root / raw).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f'evidence file missing: {raw}')
    return raw


def _count(value, label):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f'{label} must be a non-negative integer')
    return value


def token_total(tokens):
    if tokens is None:
        return None
    if not isinstance(tokens, dict):
        raise ValueError('coordinator_tokens must be an object')
    values = {key: _count(tokens.get(key), f'coordinator_tokens.{key}') for key in ('input', 'output', 'total')}
    cached = _count(tokens.get('cached_input', 0), 'coordinator_tokens.cached_input')
    if cached > values['input'] or values['total'] != values['input'] + values['output']:
        raise ValueError('coordinator token fields are inconsistent')
    return values['total']


def judge(record, root):
    if record.get('schema') != SCHEMA:
        raise ValueError(f'Expected schema {SCHEMA}')
    arm = record.get('arm')
    goal_id = record.get('goal_id')
    if arm not in ARMS or not isinstance(goal_id, str) or not goal_id:
        raise ValueError('arm or goal_id is invalid')
    evidence = evidence_file(root, record)
    hosted = _count(record.get('hosted_model_calls'), 'hosted_model_calls')
    if arm == HYPOTHESIS and hosted != 0:
        raise ValueError('Hypothesis arm recorded a hosted model call')
    blocked = record.get('blocked', False)
    if not isinstance(blocked, bool):
        raise ValueError('blocked must be boolean')
    lever = record.get('lever', 'measurement')
    if not isinstance(lever, str) or not lever:
        raise ValueError('lever must be a string')
    done = record.get('done_choice')
    if done is not None and not isinstance(done, bool):
        raise ValueError('done_choice must be boolean')
    if blocked:
        if not isinstance(record.get('reason'), str) or not record['reason']:
            raise ValueError('blocked record needs a reason')
        return {'arm': arm, 'goal_id': goal_id, 'passed': False, 'blocked': True, 'done_choice': done,
                'latency_ms': None, 'steps': None, 'tokens': None, 'peak_memory_bytes': None,
                'hosted_model_calls': hosted, 'lever': lever, 'category': None, 'evidence_path': evidence}
    checks = record.get('independent_checks')
    if not isinstance(checks, dict) or not checks or not all(isinstance(value, bool) for value in checks.values()):
        raise ValueError('independent_checks must be a non-empty boolean map')
    passed = all(checks.values())
    if arm in GROK_ARMS and passed and hosted < 1:
        raise ValueError('A passing Grok arm must record at least one hosted call')
    latency = record.get('latency_ms')
    if isinstance(latency, bool) or not isinstance(latency, (int, float)) or latency <= 0:
        raise ValueError('latency_ms must be positive')
    steps = _count(record.get('steps'), 'steps')
    memory = record.get('peak_memory_bytes')
    if memory is not None:
        memory = _count(memory, 'peak_memory_bytes')
    category = None
    failed = record.get('first_failed_step')
    if failed is not None:
        if not isinstance(failed, dict) or not isinstance(failed.get('category'), str) or not failed['category']:
            raise ValueError('first_failed_step.category must be a string')
        category = failed['category']
    return {'arm': arm, 'goal_id': goal_id, 'passed': passed, 'blocked': False, 'done_choice': done,
            'latency_ms': latency, 'steps': steps, 'tokens': token_total(record.get('coordinator_tokens')),
            'peak_memory_bytes': memory, 'hosted_model_calls': hosted, 'lever': lever,
            'category': category, 'evidence_path': evidence}


def _median(values):
    return statistics.median(values) if values else None


def _ratio(baseline, hypothesis):
    if baseline is None or hypothesis in (None, 0):
        return None
    return baseline / hypothesis


def _token_median(rows):
    if not rows or any(row['tokens'] is None for row in rows):
        return None
    return _median([row['tokens'] for row in rows])


def arm_stats(rows):
    live = [row for row in rows if not row['blocked']]
    passed = [row for row in live if row['passed']]
    memory = [row['peak_memory_bytes'] for row in live if row['peak_memory_bytes'] is not None]
    return {'attempts': len(live), 'blocked': sum(row['blocked'] for row in rows), 'passes': len(passed),
            'success_rate': (len(passed) / len(live)) if live else None,
            'latency_ms_median_pass': _median([row['latency_ms'] for row in passed]),
            'steps_median_pass': _median([row['steps'] for row in passed]),
            'coordinator_tokens_median_pass': _token_median(passed),
            'peak_memory_bytes_max': max(memory) if memory else None,
            'evidence_paths': [row['evidence_path'] for row in rows]}


def speedups_for(judged):
    found = {}
    goals = sorted({row['goal_id'] for row in judged})
    for goal in goals:
        found[goal] = {}
        hypothesis = [row for row in judged if row['goal_id'] == goal and row['arm'] == HYPOTHESIS and row['passed']]
        for baseline in BASELINES:
            base = [row for row in judged if row['goal_id'] == goal and row['arm'] == baseline and row['passed']]
            comparable = bool(hypothesis and base)
            found[goal][baseline] = {
                'comparable': comparable,
                'latency': _ratio(_median([row['latency_ms'] for row in base]),
                                  _median([row['latency_ms'] for row in hypothesis])) if comparable else None,
                'steps': _ratio(_median([row['steps'] for row in base]),
                                _median([row['steps'] for row in hypothesis])) if comparable else None,
                'tokens': _ratio(_token_median(base), _token_median(hypothesis)) if comparable else None,
                'hypothesis_evidence': [row['evidence_path'] for row in hypothesis],
                'baseline_evidence': [row['evidence_path'] for row in base]}
    return found


def _recommendation(action, lever, goal_id, reason, alive, arms=None):
    result = {'action': action, 'lever': lever, 'goal_id': goal_id, 'reason': reason, 'hypothesis_alive': alive}
    if arms:
        result['arms'] = arms
    return result


def recommend(judged, speedups):
    if not judged:
        return _recommendation('collect-baselines', 'none', PRIMARY,
                               'No measured runs yet. Record one independently judged attempt for each arm '
                               'before changing code.', True, list(ARMS))
    local = [row for row in judged if row['arm'] == HYPOTHESIS and row['goal_id'] == PRIMARY]
    if not local:
        return _recommendation('collect-baselines', 'none', PRIMARY,
                               'The local coordinator has no primary-goal record yet.', True, [HYPOTHESIS])
    if any(not row['passed'] and not row['blocked'] and not row['category'] for row in local):
        return _recommendation('record-failure-category', 'none', PRIMARY,
                               'A failed local-search run has no first-failed-step category. '
                               'Record it before changing code.', True)
    present = {row['arm'] for row in judged if row['goal_id'] == PRIMARY and row['arm'] in BASELINES}
    missing = [arm for arm in BASELINES if arm not in present]
    if missing:
        return _recommendation('collect-baselines', 'none', PRIMARY,
                               'Record the missing baseline arms before changing a lever.', True, missing)
    levers = {row['lever'] for row in local}
    live = [row for row in local if not row['blocked']]
    if live and not any(row['passed'] for row in live):
        category = next(row['category'] for row in reversed(live) if not row['passed'])
        wanted = LEVER_FOR_CATEGORY.get(category)
        if wanted and wanted not in levers:
            return _recommendation('change-one-lever', wanted, PRIMARY,
                                   f'The latest failure category is {category}. Change only the {wanted} lever.', True)
        if wanted and wanted in levers and len(live) >= 3:
            return _recommendation('stop', 'none', PRIMARY,
                                   f'Local search still failed after the {wanted} lever. '
                                   'This line needs a different approach.', False)
        if wanted is None:
            return _recommendation('hold', 'none', PRIMARY,
                                   f'Failure category {category} has no authorized lever. Do not invent one.', True)
    consecutive = 0
    for row in reversed(local):
        if row['blocked']:
            continue
        if not row['passed']:
            break
        consecutive += 1
    if consecutive < 3:
        return _recommendation('repeat-goal', 'none', PRIMARY,
                               'Keep the same goal until three consecutive independently passing local runs.', True)
    comparable = [item for item in speedups.get(PRIMARY, {}).values() if item['comparable']]
    slower = [item for item in comparable if item['latency'] is not None and item['latency'] < 1]
    if slower and 'caching' not in levers:
        return _recommendation('change-one-lever', 'caching', PRIMARY,
                               'Passing runs are slower than a comparable baseline. Change only caching.', True)
    if comparable and len(slower) == len(comparable) and 'caching' in levers:
        return _recommendation('stop', 'none', PRIMARY,
                               'Caching still left the local coordinator slower than every comparable baseline. '
                               'This line needs a different approach.', False)
    if slower:
        return _recommendation('next-line', 'design', PRIMARY,
                               'Caching did not beat every comparable baseline. Start a new line instead of '
                               'stacking another lever on this one.', True)
    return _recommendation('run-variation', 'none', VARIATION,
                           'Three consecutive local passes. Run the reordered layout before any live flight goal.',
                           True)


def load_records(directory):
    paths = sorted(path for path in directory.rglob('*.json') if path.is_file())
    if not paths:
        raise FileNotFoundError(f'No run records in {directory}')
    records = []
    for path in paths:
        data = json.loads(path.read_text())
        if not isinstance(data, dict) or data.get('schema') != SCHEMA:
            raise ValueError(f'{path.name} is not a {SCHEMA} record')
        records.append(data)
    return records


def summarize(records, root):
    judged = [judge(record, root) for record in records]
    grouped = {}
    for row in judged:
        grouped.setdefault((row['arm'], row['goal_id']), []).append(row)
    speedups = speedups_for(judged)
    recommendation = recommend(judged, speedups)
    return {'schema_version': 1, 'runs': judged,
            'arms': {f'{arm}:{goal}': arm_stats(rows) for (arm, goal), rows in sorted(grouped.items())},
            'speedups': speedups, 'next_lever': recommendation,
            'hypothesis_alive': recommendation['hypothesis_alive'],
            'limits': ['DONE is ignored. Pass requires every independent check to be true.',
                       'Latency, token, and step ratios use passing runs only.',
                       'A ratio above 1 means the local coordinator used less of that resource.',
                       'Missing evidence, inconsistent tokens, or a hosted hypothesis call reject the batch.',
                       'These ratios are only as comparable as the recorded goals and timing boundaries.']}


def combined_score(summary):
    ratios = [item['latency'] for goal in summary['speedups'].values() for item in goal.values()
              if item['comparable'] and item['latency'] is not None]
    if not ratios or not summary['hypothesis_alive']:
        return 0.0
    return min(ratios)


def _metric_key(text):
    return ''.join(char if char.isalnum() or char in '-_.' else '_' for char in text)


def flat_metrics(summary):
    metrics = {}
    for key, stats in summary['arms'].items():
        name = _metric_key(key)
        for field in ('success_rate', 'latency_ms_median_pass', 'steps_median_pass',
                      'coordinator_tokens_median_pass', 'peak_memory_bytes_max'):
            if stats[field] is not None:
                metrics[f'{name}.{field}'] = stats[field]
    for goal, baselines in summary['speedups'].items():
        for baseline, item in baselines.items():
            if item['latency'] is None:
                continue
            metrics[_metric_key(f'{goal}.{baseline}.latency')] = item['latency']
    return metrics


def log_mlflow(summary, tracking_uri, artifact):
    import mlflow
    mlflow.set_tracking_uri(str(tracking_uri))
    mlflow.set_experiment('zero-browser-local-coordinator')
    with mlflow.start_run(run_name='experiment-loop'):
        for key, value in flat_metrics(summary).items():
            mlflow.log_metric(key, float(value))
        mlflow.log_artifact(str(artifact))
    return {'logged': True, 'tracking_uri': str(tracking_uri)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', type=Path, default=ROOT / 'results' / 'experiment-loop')
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--mlflow', type=Path)
    args = parser.parse_args(argv)
    if not args.runs.is_dir():
        print(f'No experiment directory: {args.runs}', file=sys.stderr)
        return 2
    try:
        records = load_records(args.runs)
        summary = summarize(records, args.root)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 2
    text = json.dumps(summary, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    if args.mlflow:
        if not args.output:
            print('--mlflow requires --output so the logged artifact exists', file=sys.stderr)
            return 2
        try:
            print(json.dumps(log_mlflow(summary, args.mlflow, args.output)))
        except ImportError:
            print('mlflow is not installed; wrote the JSON summary without a tracking run', file=sys.stderr)
    print(text, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
