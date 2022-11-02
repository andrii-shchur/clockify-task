import configparser
import json
import requests


def get_api_key():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['auth']['api_key']


def get_workspace_ids():
    r = requests.get(f'https://api.clockify.me/api/v1/workspaces/',
                     headers={'x-api-key': get_api_key()})
    d = json.loads(r.content)
    return [el['id'] for el in d]


def get_user_id():
    r = requests.get(f'https://api.clockify.me/api/v1/user/',
                     headers={'x-api-key': get_api_key()})
    d = json.loads(r.content)
    return d['id']
