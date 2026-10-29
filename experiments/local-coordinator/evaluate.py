"""Write AI-Scientist metrics for already recorded browser runs. Does not launch a browser or a model."""

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('experiment_scoreboard', ROOT / 'scripts' / 'experiment_scoreboard.py')
board = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(board)


def main(records_dir, results_dir, root):
    results = Path(results_dir)
    results.mkdir(parents=True, exist_ok=True)
    correct = False
    message = None
    try:
        summary = board.summarize(board.load_records(Path(records_dir)), Path(root))
        score = board.combined_score(summary)
        metrics = {'combined_score': score, 'public': {'hypothesis_alive': summary['hypothesis_alive'],
                   'next_lever': summary['next_lever'], 'speedups': summary['speedups']}}
        correct = True
        message = summary['next_lever']['reason']
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        metrics = {'combined_score': 0.0, 'error': str(error)}
        message = str(error)
    (results / 'metrics.json').write_text(json.dumps(metrics, indent=2) + '\n')
    (results / 'correct.json').write_text(json.dumps({'correct': correct, 'message': message}, indent=2) + '\n')
    return 0 if correct else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--records', type=Path, required=True)
    parser.add_argument('--results_dir', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    raise SystemExit(main(args.records, args.results_dir, args.root))
