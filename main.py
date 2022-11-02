import requests
import json
from utils import get_user_id, get_workspace_ids, get_api_key

api_key = get_api_key()
workspace_ids = get_workspace_ids()
user_id = get_user_id()

headers = {'x-api-key': api_key}
result = []
for workspace_id in workspace_ids:
    r = requests.get(f'https://api.clockify.me/api/v1/workspaces/{workspace_id}/user/{user_id}/time-entries',
                     headers=headers)
    result.extend(json.loads(r.content))

with open('res.json', 'w') as f:
    json.dump(result, f, indent=4)
