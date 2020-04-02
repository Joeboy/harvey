#!/usr/bin/env python3
"""
Only the people who are working the victory by faith will experience the joy
of harvest. - Sunday Adelaja
"""

import datetime
import json
import re
import urllib
from argparse import ArgumentParser
from collections import defaultdict

import requests

import settings

DATE_RE = re.compile(r'^.*(?P<isodate>202\d-\d\d-\d\d)$')
ENTRY_RE = re.compile(r'^(?P<hours>[\d\.]+) +(?P<ticket_no>SCOPE-\d\d\d\d\d?): (?P<description>.*)$')
COMMENT_RE = re.compile(r'^[\t ]*#')


class ApiRequester(object):
    def __init__(self):
        pass

    def get_full_api_url(self, path):
        return urllib.parse.urljoin(settings.API_ROOT, path)

    def get_headers(self):
        headers = {
            'Harvest-Account-ID': settings.ACCOUNT_ID,
            'Authorization': 'Bearer {}'.format(settings.PERSONAL_ACCESS_TOKEN),
            'User-Agent': settings.USER_AGENT,
        }
        return headers

    def get(self, path, params=None):
        return requests.get(
            self.get_full_api_url(path),
            params=params,
            headers=self.get_headers(),
        )

    def post(self, path, json=None):
        return requests.post(
            self.get_full_api_url(path),
            json=json,
            headers=self.get_headers(),
        )


api_requester = ApiRequester()


def pp_dict(d):
    print(json.dumps(d, indent=4))


def parse_date_line(line):
    m = DATE_RE.match(line)
    if m:
        return m.group(1)


def parse_ticket_line(line):
    m = ENTRY_RE.match(line)
    if m:
        data = m.groupdict()
        data['hours'] = float(data['hours'])
        return data


def get_next_line(f):
    while True:
        line = next(f).strip()
        if not COMMENT_RE.match(line):
            return line


def get_dates_already_entered():
    from_datetime = datetime.datetime.now() - datetime.timedelta(days=100)
    from_str = from_datetime.date().isoformat()
    r = api_requester.get(
        "/v2/time_entries",
        params={
            'user_id': settings.USER_ID,
            'from': from_str,
        }
    )
    time_entries = r.json()['time_entries']
    # pp_dict(time_entries[0])
    return [e['spent_date'] for e in time_entries]


def main(args):
    entries_by_date = defaultdict(list)
    with open(args.filename) as f:
        try:
            line = get_next_line(f)
            while True:
                iso_date = parse_date_line(line)
                if iso_date is None:
                    line = get_next_line(f)
                    continue

                hours_for_date = 0
                line = get_next_line(f)
                while True:
                    entry_data = parse_ticket_line(line)
                    if entry_data is None:
                        # Not a ticket line, assume end of entries for date
                        line = get_next_line(f)
                        break

                    entries_by_date[iso_date].append(entry_data)
                    hours_for_date += entry_data['hours']
                    line = get_next_line(f)

        except StopIteration:
            print("Done parsing file")

    found_dates = list(entries_by_date.keys())
    dates_already_entered = get_dates_already_entered()
    for found_date in found_dates:
        has_issues = False
        hours_for_date = sum((e['hours'] for e in entries_by_date[found_date]))
        if hours_for_date != 8:
            print("Warning: Logged {} hours for {}, not 8".format(hours_for_date, found_date))
            has_issues = True

        if found_date in dates_already_entered:
            print("WARNING: ignoring date {} as it has already been entered into harvest".format(found_date))
            entries_by_date.pop(found_date)
            has_issues = True
        if not has_issues:
            print("Looks good: {}".format(found_date))
    print("Total days for timesheet: {}".format(len(found_dates)))

    if args.submit:
        for date, entries_data in entries_by_date.items():
            for entry_data in entries_data:
                entry_json = {
                    'project_id': settings.PROJECT_ID,
                    'task_id': settings.TASK_ID,
                    'spent_date': date,
                    'notes': "{}: {}".format(entry_data['ticket_no'], entry_data['description']),
                    'hours': entry_data['hours'],
                }
                print(entry_json)
                r = api_requester.post(
                    "/v2/time_entries",
                    json=entry_json,
                )
                print(r)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '--file',
        nargs='?',
        dest='filename',
        required=True,
        help='Filename'
    )
    parser.add_argument(
        "--submit",
        action='store_true',
        help="Set this to TRUE to submit timesheet data to harvest."
    )

    args = parser.parse_args()
    main(args)
