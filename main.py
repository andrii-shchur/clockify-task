from datetime import datetime, timedelta

import requests
import json
from functools import reduce

from utils import get_user_id, get_workspace_ids, get_api_key, TimeParse


# Get metadata
api_key = get_api_key()
workspace_ids = get_workspace_ids()
user_id = get_user_id()

# Get all entries using API
headers = {'x-api-key': api_key}
result = []
for workspace_id in workspace_ids:
    r = requests.get(f'https://api.clockify.me/api/v1/workspaces/{workspace_id}/user/{user_id}/time-entries',
                     headers=headers)
    result.extend(json.loads(r.content))

# Dump all entries into res.json
with open('res.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

grouped = {}
days = set()
for el in result:
    # Transform datetime strings into datetime objects
    # This will help perform some actions
    datetime_start = el['timeInterval']['start'].replace('T', ' ').replace('Z', '')
    el['timeInterval']['start'] = datetime.strptime(datetime_start, '%Y-%m-%d %H:%M:%S')
    if el['timeInterval']['end']:
        datetime_end = el['timeInterval']['end'].replace('T', ' ').replace('Z', '')
        el['timeInterval']['end'] = datetime.strptime(datetime_end, '%Y-%m-%d %H:%M:%S')

    # Find all dates among entries
    days.add(el['timeInterval']['start'].date())
    if el['timeInterval']['end']:
        days.add(el['timeInterval']['end'].date())

    # Group entries by taskId
    try:
        grouped[el['taskId']].append({'description': el['description'], 'timeInterval': el['timeInterval']})
    except KeyError:
        grouped[el['taskId']] = []
        grouped[el['taskId']].append({'description': el['description'], 'timeInterval': el['timeInterval']})

# Time spent on each task
print('Time spent on each task: ')
for key, value in grouped.items():
    print(f'taskId: {key}\n'
          f'description: {value[0]["description"]}\n'
          f'total time: {reduce(lambda x, y: x + y, [TimeParse(el["timeInterval"]["duration"]) for el in value])}\n')

print('----------------------------\n')
print('Time spent each day: ')

# Time spent each day
time_each_day = dict([(el, timedelta(0)) for el in days])
for day in days:
    for el in result:
        st = el['timeInterval']['start']
        if not (end := el['timeInterval']['end']):
            end = datetime.strptime(datetime.now().isoformat(' ', 'seconds'), '%Y-%m-%d %H:%M:%S')

        if st.date() == day:
            if end.date() == day:
                duration = TimeParse(el['timeInterval']['duration'])
                time_each_day[day] += timedelta(hours=duration.h, minutes=duration.m, seconds=duration.s)
            else:
                tmp = day + timedelta(days=1)
                time_each_day[day] += datetime(tmp.year, tmp.month, tmp.day, 0, 0, 0) - st
        elif end.date() == day:
            time_each_day[day] += end - datetime(day.year, day.month, day.day, 0, 0, 0)

# Prettify and sort by date
time_each_day = time_each_day.items()
time_each_day = sorted(time_each_day, key=lambda x: x[0])
time_each_day = list(map(lambda x: (str(x[0]), str(x[1])), time_each_day))

for key, value in time_each_day:
    print(f'{key} - {value}')
