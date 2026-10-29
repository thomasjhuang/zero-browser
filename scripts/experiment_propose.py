"""Emit one AI-Scientist v3 idea from scored records. No records, no idea."""

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('experiment_scoreboard', ROOT / 'scripts' / 'experiment_scoreboard.py')
board = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(board)
RUBRICS = ROOT / 'experiments' / 'local-coordinator' / 'rubrics.json'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', type=Path, default=ROOT / 'results' / 'experiment-loop')
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--rubrics', type=Path, default=RUBRICS)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    if not args.runs.is_dir():
        print(f'No experiment directory: {args.runs}', file=sys.stderr)
        return 2
    try:
        summary = board.summarize(board.load_records(args.runs), args.root)
        idea = board.propose_idea(summary, json.loads(args.rubrics.read_text()))
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 2
    text = json.dumps(idea, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
