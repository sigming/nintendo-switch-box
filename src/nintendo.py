import base64
import hashlib
import json
import os
import re
import urllib.parse

import requests

REQUEST_TIMEOUT = 30


# https://github.com/raycast/extensions/blob/main/extensions/switch-game-play-history/src/helpers/nintendo.ts
# https://github.com/frozenpandaman/splatnet2statink/blob/master/iksm.py
# https://ar1s.top/2022/08/01/%E8%8E%B7%E5%8F%96switch%E6%B8%B8%E6%88%8F%E5%8E%86%E5%8F%B2%E7%9A%84%E4%B8%80%E7%A7%8D%E6%96%B9%E6%B3%95/
# https://github.com/kinnay/NintendoClients/wiki/Account-Server-(Switch)#user-agents
# https://github.com/ZekeSnider/NintendoSwitchRESTAPI
# https://github.com/ChengChung/nscard


class NintendoClient:
    def __init__(self, session_token=None):
        self.app_version = '3.0.3'
        self.session_token = session_token
        # My Nintendo client_id (for play history API)
        self.client_id = '5c38e31cd085304b'

    def get_play_histories(self):
        api = 'https://app-api.znej.nintendo.com/api/v2.0/users/me/play_histories'
        api_token = self.get_api_token()
        if not api_token:
            print('Failed to get API token.')
            return None

        access_token = api_token['access_token']
        headers = {
            'User-Agent': f'com.nintendo.znej/{self.app_version} (iOS/26.0.1)',
            'Authorization': f'Bearer {access_token}',
            'gentry-locale': 'en-US'  # ja-JP
        }
        r = requests.get(api, headers=headers, timeout=REQUEST_TIMEOUT)
        if r.status_code != 200:
            print(f'Failed to get play histories. Status: {r.status_code}, Response: {r.text}')
            return None
        return r.json()

    @staticmethod
    def get_game_title(title_id, region='US'):
        url = f'https://ec.nintendo.com/apps/{title_id}/{region}'
        r = requests.get(url, allow_redirects=True, timeout=REQUEST_TIMEOUT)
        if r.status_code != 200:
            return {}

        pattern = r'<script type="application/ld\+json">(.*?)<\/script>'
        match = re.search(pattern, r.text, re.DOTALL)
        if match:
            game_info = json.loads(match.group(1))
            if '@graph' in game_info:
                return game_info['@graph'][0]
            else:
                return game_info
        else:
            pattern = r'<title data-react-helmet="true">(.*?)\|'
            match = re.search(pattern, r.text, re.DOTALL)
            if match:
                return {'name': match.group(1).strip()}
            return {}

    def get_api_token(self):
        if not self.session_token:
            print("No session token found. Please log in first.")
            return None

        app_head = {
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': f'com.nintendo.znej/{self.app_version} (iOS/26.0.1)'
        }

        body = {
            'client_id': self.client_id,
            'session_token': self.session_token,
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer-session-token'
        }

        url = 'https://accounts.nintendo.com/connect/1.0.0/api/token'
        r = requests.post(url, headers=app_head, json=body, timeout=REQUEST_TIMEOUT)

        try:
            container = json.loads(r.text)
            api_token_info = {
                'id_token': container['id_token'],
                'access_token': container['access_token'],
                'expires_in': container['expires_in']
            }
            return api_token_info

        except json.decoder.JSONDecodeError:
            print("Got non-JSON response from Nintendo (in api/token step). Please try again.")
            return None

    def get_nso_login_info(self):
        auth_state = base64.urlsafe_b64encode(os.urandom(36))

        auth_code_verifier = base64.urlsafe_b64encode(os.urandom(32))
        auth_cv_hash = hashlib.sha256()
        auth_cv_hash.update(auth_code_verifier.replace(b'=', b''))
        auth_code_challenge = base64.urlsafe_b64encode(auth_cv_hash.digest())

        body = {
            'state': auth_state,
            'redirect_uri': f'npf{self.client_id}://auth',
            'client_id': self.client_id,
            'scope': 'openid user user.mii user.email user.links[].id',
            'response_type': 'session_token_code',
            'session_token_code_challenge': auth_code_challenge.replace(b'=', b''),
            'session_token_code_challenge_method': 'S256',
            'theme': 'login_form'
        }

        info = {
            'auth_code_verifier': auth_code_verifier,
            'login_url': f'https://accounts.nintendo.com/connect/1.0.0/authorize?{urllib.parse.urlencode(body)}'
        }
        return info

    def get_session_token(self, session_token_code, auth_code_verifier):
        app_head = {
            'User-Agent': f'com.nintendo.znej/{self.app_version} (iOS/26.0.1)',
            'Accept-Language': 'en-US',
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'accounts.nintendo.com',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip'
        }

        body = {
            'client_id': self.client_id,
            'session_token_code': session_token_code,
            'session_token_code_verifier': auth_code_verifier.replace(b'=', b'')
        }

        url = 'https://accounts.nintendo.com/connect/1.0.0/api/session_token'

        r = requests.post(url, headers=app_head, data=body, timeout=REQUEST_TIMEOUT)
        try:
            container = json.loads(r.text)
            session_token = container['session_token']
            self.session_token = session_token
            # exp 2 years

        except json.decoder.JSONDecodeError:
            print("Got non-JSON response from Nintendo (in api/session_token step). Please try again.")
            return None

        except KeyError:
            print("\nThe URL has expired. Logging out & back in to your Nintendo Account and retrying may fix this.")
            print("Error from Nintendo (in api/session_token step):")
            print(r.text)
            return None

        return session_token
