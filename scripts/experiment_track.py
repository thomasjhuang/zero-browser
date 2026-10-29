"""Log a scored experiment batch to a local MLflow file store. No records, no run."""

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('experiment_scoreboard', ROOT / 'scripts' / 'experiment_scoreboard.py')
board = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(board)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', type=Path, default=ROOT / 'artifacts' / 'experiment-loop')
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--mlflow', type=Path, default=ROOT / 'artifacts' / 'mlflow')
    args = parser.parse_args(argv)
    if not args.runs.is_dir():
        print(f'No experiment directory: {args.runs}', file=sys.stderr)
        return 2
    if args.output is None:
        print('--output is required so the logged artifact is an explicit file', file=sys.stderr)
        return 2
    try:
        summary = board.summarize(board.load_records(args.runs), args.root)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + '\n')
    try:
        print(json.dumps(board.log_mlflow(summary, args.mlflow, args.output)))
    except ImportError:
        print('mlflow is not installed', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
