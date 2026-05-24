"""
Zoho OAuth2 авторизація для Zoho Forms API.
Запустіть один раз для отримання токенів.
"""

import webbrowser
import json
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

CLIENT_ID = '1000.N3DATFNJ7WPHKHB5C2HI5STZ1QTLEG'
CLIENT_SECRET = '323df6e182b83a44aed613ced4d651b30b2d9ed942'
REDIRECT_URI = 'http://localhost:8080'
TOKENS_FILE = Path(__file__).parent / 'zoho_tokens.json'

captured_code = None


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global captured_code
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if 'code' in params:
            captured_code = params['code'][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'<h2>Authorized! You can close this tab.</h2>')
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'<h2>Error: no code received.</h2>')

    def log_message(self, format, *args):
        pass


def authorize():
    params = urllib.parse.urlencode({
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'scope': 'ZohoForms.fullaccess.all',
        'redirect_uri': REDIRECT_URI,
        'access_type': 'offline',
    })
    url = f'https://accounts.zoho.com/oauth/v2/auth?{params}'
    print(f'Opening browser for Zoho authorization...')
    webbrowser.open(url)

    server = HTTPServer(('localhost', 8080), CallbackHandler)
    server.handle_request()

    if not captured_code:
        raise RuntimeError('Authorization code not received.')

    data = urllib.parse.urlencode({
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': captured_code,
    }).encode()

    req = urllib.request.Request('https://accounts.zoho.com/oauth/v2/token', data=data, method='POST')
    with urllib.request.urlopen(req) as resp:
        tokens = json.loads(resp.read())

    if 'access_token' not in tokens:
        raise RuntimeError(f'Token error: {tokens}')

    TOKENS_FILE.write_text(json.dumps(tokens, indent=2))
    print(f'Tokens saved to {TOKENS_FILE}')
    return tokens


def refresh_tokens():
    tokens = json.loads(TOKENS_FILE.read_text())
    data = urllib.parse.urlencode({
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': tokens['refresh_token'],
    }).encode()

    req = urllib.request.Request('https://accounts.zoho.com/oauth/v2/token', data=data, method='POST')
    with urllib.request.urlopen(req) as resp:
        new_tokens = json.loads(resp.read())

    new_tokens['refresh_token'] = tokens['refresh_token']
    TOKENS_FILE.write_text(json.dumps(new_tokens, indent=2))
    return new_tokens['access_token']


def get_access_token():
    if not TOKENS_FILE.exists():
        tokens = authorize()
        return tokens['access_token']
    tokens = json.loads(TOKENS_FILE.read_text())
    return tokens.get('access_token')


if __name__ == '__main__':
    authorize()
    print('Authorization complete.')
