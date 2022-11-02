import configparser
import json
import requests


# Get API key specified in config.ini
def get_api_key() -> str:
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['auth']['api_key']


# Get all workspace ids using API
def get_workspace_ids() -> list:
    r = requests.get(f'https://api.clockify.me/api/v1/workspaces/',
                     headers={'x-api-key': get_api_key()})
    d = json.loads(r.content)
    return [el['id'] for el in d]


# Get current user id using API
def get_user_id() -> str:
    r = requests.get(f'https://api.clockify.me/api/v1/user/',
                     headers={'x-api-key': get_api_key()})
    d = json.loads(r.content)
    return d['id']


# Class for time parser
class TimeParse:
    def __init__(self, time: str | None):
        self.s = self.m = self.h = 0
        if not time:
            return

        curr = ''
        for el in time.strip('PT'):
            if el == 'H':
                self.h = int(curr)
                curr = ''
            elif el == 'M':
                self.m = int(curr)
                curr = ''
            elif el == 'S':
                self.s = int(curr)
                curr = ''
            else:
                curr += el

    def __str__(self):
        return f'{self.h} hours, {self.m} minutes, {self.s} seconds'

    def __add__(self, other):
        s = (self.s + other.s) % 60
        m = (self.m + other.m + (self.s + other.s) // 60) % 60
        h = self.h + other.h + (self.m + other.m + (self.s + other.s) // 60) // 60

        return TimeParse(f'PT{h}H{m}M{s}S')
