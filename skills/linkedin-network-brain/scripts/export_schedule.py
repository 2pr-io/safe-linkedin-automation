#!/usr/bin/env python3
"""Decide whether the LinkedIn export is due, so runs land at a random 44-52h
rhythm instead of the same time every 2 days.

The scheduled task runs often (every 2 hours) and asks first:

    python3 export_schedule.py due     # prints "due", or "not due until <time>"

and after an export attempt, whatever happened:

    python3 export_schedule.py done    # picks the next time, 44 to 52 hours away

State is one line in <folder>/.next-export. Standard library only.
"""
import argparse
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('command', choices=['due', 'done'])
    ap.add_argument('--folder', type=Path, default=Path('~/Downloads/linkedin-archives'),
                    help='archive folder that holds the state file')
    ap.add_argument('--min-hours', type=float, default=44)
    ap.add_argument('--max-hours', type=float, default=52)
    args = ap.parse_args()
    if not 0 < args.min_hours <= args.max_hours:
        sys.exit('--min-hours must be positive and not above --max-hours')

    folder = args.folder.expanduser()
    state = folder / '.next-export'
    now = datetime.now().astimezone()

    next_at = None
    if state.exists():
        try:
            next_at = datetime.fromisoformat(state.read_text().strip())
        except ValueError:
            next_at = None  # unreadable state: treat as due

    if args.command == 'done':
        folder.mkdir(parents=True, exist_ok=True)
        hours = random.uniform(args.min_hours, args.max_hours)
        next_at = (now + timedelta(hours=hours)).replace(microsecond=0)
        state.write_text(next_at.isoformat() + '\n')
        print(f'next export at {next_at:%Y-%m-%d %H:%M} ({hours:.1f} hours from now)')
    elif next_at is None or now >= next_at:
        print('due')
    else:
        print(f'not due until {next_at:%Y-%m-%d %H:%M}')


if __name__ == '__main__':
    main()
