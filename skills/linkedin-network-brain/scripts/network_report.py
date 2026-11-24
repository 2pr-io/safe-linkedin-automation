#!/usr/bin/env python3
"""Turn a LinkedIn data archive into a to-do list: who you owe a reply, and which
new connections you never talked to.

    python3 network_report.py ~/Downloads/linkedin-archives/        # newest zip
    python3 network_report.py path/to/archive.zip --days 30 --out report.md

Standard library only. Reads the archive locally; nothing is uploaded.
"""
import argparse
import csv
import io
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


def open_archive(path):
    """Return a function name -> list of CSV text lines (or None), plus a label."""
    path = path.expanduser()
    if path.is_dir():
        zips = sorted(path.glob('*.zip'), key=lambda p: p.stat().st_mtime)
        if (path / 'Connections.csv').exists() or (path / 'messages.csv').exists():
            return (lambda n: _read_file(path / n)), str(path)
        if not zips:
            sys.exit(f'no LinkedIn archive (.zip) found in {path}')
        path = zips[-1]
    if not path.is_file():
        sys.exit(f'no such file: {path}')
    zf = zipfile.ZipFile(path)
    names = {Path(n).name: n for n in zf.namelist()}

    def read(name):
        if name not in names:
            return None
        return zf.read(names[name]).decode('utf-8-sig', errors='replace')
    return read, str(path)


def _read_file(p):
    return p.read_text(encoding='utf-8-sig', errors='replace') if p.exists() else None


def rows(text, header_starts):
    """CSV rows, skipping any preamble lines before the real header."""
    if text is None:
        return []
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.lstrip('"').startswith(header_starts):
            return list(csv.DictReader(io.StringIO(''.join(lines[i:]))))
    return []


def norm(url):
    return (url or '').strip().lower().rstrip('/').replace('http://', 'https://')


def parse_msg_date(s):
    try:
        return datetime.strptime(s.strip(), '%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def parse_conn_date(s):
    for fmt in ('%d %b %Y', '%m/%d/%y', '%Y-%m-%d'):
        try:
            return datetime.strptime(s.strip(), fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def is_closer(text):
    """A message that ends a conversation: an emoji, "thanks", "will do"."""
    text = (text or '').strip()
    if not any(ch.isalnum() for ch in text):
        return True
    return '?' not in text and len(text.split()) <= 5


def one_line(text, n=110):
    text = ' '.join((text or '').split())
    return text if len(text) <= n else text[: n - 1] + '…'


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('archive', type=Path, help='archive zip, unzipped folder, or folder of zips')
    ap.add_argument('--days', type=int, default=30, help='look-back window (default 30)')
    ap.add_argument('--limit', type=int, default=25, help='max rows per section (default 25)')
    ap.add_argument('--out', type=Path, help='also write the report to this file')
    args = ap.parse_args()

    read, label = open_archive(args.archive)
    messages = rows(read('messages.csv'), 'CONVERSATION ID')
    connections = rows(read('Connections.csv'), 'First Name')
    if not messages and not connections:
        sys.exit('this archive has no messages.csv or Connections.csv; request the full ("larger") archive')

    messages = [m for m in messages
                if m.get('IS MESSAGE DRAFT', 'No') != 'Yes' and m.get('FOLDER') != 'SPAM']
    for m in messages:
        m['_at'] = parse_msg_date(m.get('DATE', ''))
    messages = [m for m in messages if m['_at']]

    # You are whoever sends the most messages in your own archive.
    me = Counter(norm(m.get('SENDER PROFILE URL')) for m in messages).most_common(1)
    me = me[0][0] if me else ''

    now = max([m['_at'] for m in messages], default=datetime.now(timezone.utc))
    since = now - timedelta(days=args.days)

    by_conv = defaultdict(list)
    talked_to = set()
    for m in messages:
        by_conv[m['CONVERSATION ID']].append(m)
        for u in [m.get('SENDER PROFILE URL', '')] + m.get('RECIPIENT PROFILE URLS', '').split(','):
            if norm(u) and norm(u) != me:
                talked_to.add(norm(u))

    warm, cold, closers = [], [], 0
    for conv in by_conv.values():
        conv.sort(key=lambda m: m['_at'])
        last = conv[-1]
        if norm(last.get('SENDER PROFILE URL')) == me or last['_at'] < since:
            continue
        if is_closer(last.get('CONTENT', '')):
            closers += 1
            continue
        i_replied = any(norm(m.get('SENDER PROFILE URL')) == me for m in conv)
        item = (last['_at'], last.get('FROM', '').strip() or '(unknown)',
                last.get('SENDER PROFILE URL', ''), last.get('CONTENT') or last.get('SUBJECT', ''))
        (warm if i_replied else cold).append(item)
    # Open questions first, then newest.
    warm.sort(key=lambda it: ('?' in it[3], it[0]), reverse=True)
    cold.sort(reverse=True)

    new_silent = []
    for c in connections:
        at = parse_conn_date(c.get('Connected On', ''))
        if not at or at < since or norm(c.get('URL')) in talked_to:
            continue
        name = f"{c.get('First Name', '')} {c.get('Last Name', '')}".strip() or '(hidden)'
        role = ', '.join(x for x in (c.get('Position', '').strip(), c.get('Company', '').strip()) if x)
        new_silent.append((at, name, c.get('URL', ''), role))
    new_silent.sort(reverse=True)
    new_total = sum(1 for c in connections
                    if (d := parse_conn_date(c.get('Connected On', ''))) and d >= since)

    out = [f'# LinkedIn network report, last {args.days} days',
           f'Archive: {label}  ',
           f'Newest message in archive: {now:%Y-%m-%d}', '',
           f'- {len(warm)} people you talked to before are waiting on your reply',
           f'- {len(cold)} people wrote to you and never got an answer',
           f'- {len(new_silent)} of {new_total} new connections have never heard from you',
           f'- {closers} conversations ended on a "thanks" or an emoji, so they are left out', '']

    def section(title, items, fmt):
        out.append(f'## {title} ({len(items)})')
        if not items:
            out.append('Nothing here.')
        for it in items[: args.limit]:
            out.append(fmt(it))
        if len(items) > args.limit:
            out.append(f'...and {len(items) - args.limit} more (use --limit to see them)')
        out.append('')

    msg_fmt = lambda it: f'- {it[0]:%Y-%m-%d} **{it[1]}** {it[2]}\n  > {one_line(it[3])}'
    section('Owe a reply (warm)', warm, msg_fmt)
    section('Owe a reply (cold inbound)', cold, msg_fmt)
    section('New connections you never talked to', new_silent,
            lambda it: f'- {it[0]:%Y-%m-%d} **{it[1]}**{" (" + it[3] + ")" if it[3] else ""} {it[2]}')
    if not messages:
        out.append('No messages.csv in this archive: request the full ("larger") archive to see replies.')

    report = '\n'.join(out)
    print(report)
    if args.out:
        args.out.expanduser().write_text(report + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
