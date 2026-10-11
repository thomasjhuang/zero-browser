"""Audit preserved decisions and write the comparison without model requests."""

import argparse
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path

from decision_baselines import ROOT, SYSTEM, suite


def prompt_tokens(provider, measurement):
    usage = measurement['usage']
    if provider == 'claude':
        return sum(usage.get(key, 0) for key in
                   ['input_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens'])
    return usage['input_tokens']


def summarize(root):
    jobs, hashes = suite([root / 'fixtures/decision_cases.json', root / 'fixtures/decision_quality_cases.json'])
    expected = {(c['name'], r): (c['expected_action'], [a['id'] for a in actions],
                hashlib.sha256(prompt.encode()).hexdigest()) for c, r, actions, prompt in jobs}
    rows = []
    sources = {}
    for provider, names in [('qwen', ['decision-smoke.json', 'decision-quality.json']),
                            ('codex', ['decision-codex.json']), ('claude', ['decision-claude.json'])]:
        reports = []
        measurements = []
        for name in names:
            path = root / 'results' / name
            sources[name] = hashlib.sha256(path.read_bytes()).hexdigest()
            report = json.loads(path.read_text())
            if report['status'] != 'completed':
                raise ValueError(f'{name} is incomplete')
            if provider != 'qwen':
                if report['fixture_sha256'] != hashes:
                    raise ValueError('Fixture hashes differ')
                if report['system_sha256'] != hashlib.sha256(SYSTEM.encode()).hexdigest():
                    raise ValueError('System prompts differ')
            reports.append(report)
            measurements.extend(m for m in report['measurements'] if m.get('repetition', 0) == 0)
        if len(measurements) != len(expected):
            raise ValueError(f'{provider} has a different decision count')
        seen = set()
        per_case = defaultdict(lambda: {'correct': 0, 'total': 0})
        for m in measurements:
            key = (m['case'], m['rotation'])
            if key in seen or key not in expected:
                raise ValueError('Duplicate or unexpected decision')
            seen.add(key)
            answer, order, prompt_hash = expected[key]
            if m['expected_action'] != answer or m['candidate_order'] != order:
                raise ValueError('Answer keys or candidate orders differ')
            if provider != 'qwen' and m['user_prompt_sha256'] != prompt_hash:
                raise ValueError('User prompts differ')
            selected = m['selected_action']['id'] if provider == 'qwen' else m['selected_action']
            if m['correct'] != (selected == answer):
                raise ValueError('Correctness calculation differs')
            if provider != 'qwen' and (not m['valid_response'] or m['tool_calls']):
                raise ValueError('CLI output was invalid or used a tool')
            per_case[m['case']]['correct'] += int(m['correct'])
            per_case[m['case']]['total'] += 1
        if provider == 'qwen':
            times = [m['inference_ms'] for m in measurements if m['phase'] == 'warm_forward']
            extra = {'latency_scope': 'Warm full prompt prefill, excluding tokenization and model load',
                     'cold_first_forward_ms': [r['cold_first_forward_ms'] for r in reports],
                     'model_load_ms': [r['model_load_ms'] for r in reports],
                     'peak_mlx_bytes': max(r['peak_mlx_bytes'] for r in reports),
                     'prompt_tokens_range': [min(m['prompt_tokens'] for m in measurements),
                                             max(m['prompt_tokens'] for m in measurements)],
                     'model': reports[0]['model_id'], 'revision': reports[0]['model_revision']}
        else:
            times = [m['elapsed_ms'] for m in measurements]
            token_keys = ['input_tokens', 'output_tokens', 'cached_input_tokens',
                          'cache_read_input_tokens', 'cache_creation_input_tokens', 'reasoning_output_tokens']
            extra = {'latency_scope': 'CLI startup, network access, and provider computation',
                     'first_request_ms': times[0], 'subsequent_median_ms': statistics.median(times[1:]),
                     'peak_mlx_bytes': None, 'remote_peak_memory_bytes': None,
                     'model': reports[0].get('resolved_model') or reports[0]['requested_model'],
                     'model_identity_source': 'CLI resolved model' if reports[0].get('resolved_model')
                                             else 'Explicit CLI model argument',
                     'cli_version': reports[0]['cli_version'],
                     'authentication': reports[0]['authentication'],
                     'usage_totals': {k: sum((m.get('usage') or {}).get(k, 0) for m in measurements)
                                      for k in token_keys},
                     'reported_input_tokens_range': [min(m['usage']['input_tokens'] for m in measurements),
                                                     max(m['usage']['input_tokens'] for m in measurements)],
                     'effective_prompt_tokens_range': [min(prompt_tokens(provider, m) for m in measurements),
                                                       max(prompt_tokens(provider, m) for m in measurements)],
                     'api_equivalent_usd': sum(m.get('estimated_api_equivalent_usd') or 0 for m in measurements)
                                           if provider == 'claude' else None}
        rows.append({'provider': provider, 'correct': sum(m['correct'] for m in measurements),
                     'total': len(measurements), 'per_case': dict(per_case),
                     'median_latency_ms': statistics.median(times), **extra})
    return {'status': 'audited', 'fixture_sha256': hashes, 'source_sha256': sources, 'baselines': rows,
            'limits': ['Synthetic text only. No website opens and no browser actions execute.',
                       'These cases do not establish browser-task reliability.',
                       'Qwen latency and subscription CLI latency cover different operations.',
                       'CLI models use high reasoning effort. Qwen uses one forward pass.',
                       'Each request starts a new CLI session. Remote prompt caches can apply.',
                       'Codex retains global instruction and skill context. Its wrapper differs from Claude and Qwen.',
                       'CLI logits and remote peak memory are unavailable. No confidence scores are inferred.',
                       'API-equivalent cost is provider metadata, not subscription billing.',
                       'Only four cyclic candidate orders per case were tested. Repetition budgets differ.',
                       'Claude reports uncached input separately from cache reads and writes.',
                       'Codex input includes cached input.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, default=ROOT / 'results/decision-comparison.json')
    args = parser.parse_args()
    result = summarize(args.root)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
