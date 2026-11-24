#!/usr/bin/env python3
"""Turn a LinkedIn data archive into one CRM-ready CSV: a row per connection,
with your message history and a relationship status on every row.

    python3 crm_export.py ~/Downloads/linkedin-archives/            # newest zip
    python3 crm_export.py path/to/archive.zip --out linkedin-crm.csv

Import the CSV into HubSpot, Attio, Pipedrive, Notion or Google Sheets. Use
linkedin_url as the unique key so later imports update rows instead of
duplicating them. Standard library only; nothing is uploaded.
"""
import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from network_report import (  # noqa: E402
    is_closer, norm, open_archive, parse_conn_date, parse_msg_date, rows)

SENIORITY = [
    ('founder', r'\b(co-?founder|founder|owner)\b'),
    ('c-level', r'\b(ceo|cto|cfo|coo|cmo|cpo|cro|chief)\b'),
    ('vp', r'\b(vp|vice president|svp|evp)\b'),
    ('head/director', r'\b(head of|director|partner)\b'),
    ('manager', r'\b(manager|lead)\b'),
]

COLUMNS = ['first_name', 'last_name', 'linkedin_url', 'email', 'company', 'position',
           'seniority', 'connected_on', 'messages', 'last_message_at', 'last_message_from',
           'status']


def seniority(position):
    p = (position or '').lower()
    for label, pattern in SENIORITY:
        if re.search(pattern, p):
            return label
    return ''


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('archive', type=Path, help='archive zip, unzipped folder, or folder of zips')
    ap.add_argument('--out', type=Path, default=Path('linkedin-crm.csv'),
                    help='output CSV (default ./linkedin-crm.csv)')
    args = ap.parse_args()

    read, label = open_archive(args.archive)
    connections = rows(read('Connections.csv'), 'First Name')
    if not connections:
        sys.exit('this archive has no Connections.csv')
    messages = [m for m in rows(read('messages.csv'), 'CONVERSATION ID')
                if m.get('IS MESSAGE DRAFT', 'No') != 'Yes' and m.get('FOLDER') != 'SPAM']
    for m in messages:
        m['_at'] = parse_msg_date(m.get('DATE', ''))
    messages = [m for m in messages if m['_at']]
    me = Counter(norm(m.get('SENDER PROFILE URL')) for m in messages).most_common(1)
    me = me[0][0] if me else ''

    # Per person: message count and the latest message in any conversation with them.
    count = defaultdict(int)
    last = {}
    for m in messages:
        people = {norm(u) for u in [m.get('SENDER PROFILE URL', '')]
                  + m.get('RECIPIENT PROFILE URLS', '').split(',')} - {'', me}
        for p in people:
            count[p] += 1
            if p not in last or m['_at'] > last[p]['_at']:
                last[p] = m

    out_rows, statuses = [], Counter()
    for c in connections:
        url = norm(c.get('URL'))
        lm = last.get(url)
        if not lm:
            status, frm, at = 'never talked', '', ''
        else:
            frm = 'me' if norm(lm.get('SENDER PROFILE URL')) == me else 'them'
            at = lm['_at'].strftime('%Y-%m-%d')
            if frm == 'me':
                status = 'waiting on them'
            elif is_closer(lm.get('CONTENT', '')):
                status = 'closed'
            else:
                status = 'you owe a reply'
        statuses[status] += 1
        connected = parse_conn_date(c.get('Connected On', ''))
        out_rows.append({
            'first_name': c.get('First Name', '').strip(),
            'last_name': c.get('Last Name', '').strip(),
            'linkedin_url': c.get('URL', '').strip(),
            'email': c.get('Email Address', '').strip(),
            'company': c.get('Company', '').strip(),
            'position': c.get('Position', '').strip(),
            'seniority': seniority(c.get('Position')),
            'connected_on': connected.strftime('%Y-%m-%d') if connected else '',
            'messages': count.get(url, 0),
            'last_message_at': at,
            'last_message_from': frm,
            'status': status,
        })
    # Who owes a reply first, then by status; newest activity first inside each status.
    rank = {'you owe a reply': 0, 'waiting on them': 1, 'closed': 2, 'never talked': 3}
    out_rows.sort(key=lambda r: (r['last_message_at'], r['connected_on']), reverse=True)
    out_rows.sort(key=lambda r: rank[r['status']])

    path = args.out.expanduser()
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(out_rows)

    with_email = sum(1 for r in out_rows if r['email'])
    print(f'Archive: {label}')
    print(f'Wrote {len(out_rows)} connections to {path}')
    print(f'- {with_email} have an email address')
    for s in ('you owe a reply', 'waiting on them', 'closed', 'never talked'):
        print(f'- {statuses[s]} {s}')
    if not messages:
        print('No messages.csv in this archive, so every status is "never talked". '
              'Request the full archive to get message history.')


if __name__ == '__main__':
    main()
