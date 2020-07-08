from urllib.parse import urlencode

OAUTH_URL = 'https://oauth.vk.com/authorize'
OAUTH_params = {
    'client_id': 7533048,
    'display': 'popup',
    'scope': 'groups',
    'response_type': 'token',
}

if __name__ == '__main__':
    print('?'.join((OAUTH_URL, urlencode(OAUTH_params))))