import requests

REQUEST_TIMEOUT = 30


def convert_play_duration(duration):
    if not duration:
        return '0 mins'

    hours = duration // 60
    minutes = duration % 60
    if hours == 0:
        return f'{minutes} mins'
    return f'{hours} hrs {minutes} mins'


def update_gist(gist_id, github_token, content):
    url = f'https://api.github.com/gists/{gist_id}'
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {github_token}',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    if resp.status_code != 200:
        raise Exception(f'Failed to get gist: {resp.status_code} {resp.text}')
    gist = resp.json()
    file_name = list(gist['files'].keys())[0]
    data = {
        'files': {
            file_name: {
                # 'filename': 'playstation-box',
                'content': content
            }
        }
    }
    resp = requests.patch(url, headers=headers, json=data, timeout=REQUEST_TIMEOUT)
    if resp.status_code != 200:
        raise Exception(f'Failed to update gist: {resp.status_code} {resp.text}')


def truncate_strings(strings, length):
    strings = strings.strip()
    if len(strings) > length:
        return strings[:length - 3] + '...'
    else:
        return strings


def clean_game_name(name):
    return name.replace('®', '').replace('™', '').strip()
