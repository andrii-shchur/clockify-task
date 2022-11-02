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
for el in result:
    try:
        grouped[el['taskId']].append({'description': el['description'], 'timeInterval': el['timeInterval']})
    except KeyError:
        grouped[el['taskId']] = []
        grouped[el['taskId']].append({'description': el['description'], 'timeInterval': el['timeInterval']})

# Time spent on each task
for key, value in grouped.items():
    print(f'id: {key} '
          f'total time: {reduce(lambda x, y: x + y, [TimeParse(el["timeInterval"]["duration"]) for el in value])}')
