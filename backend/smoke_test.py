from __future__ import annotations

import json
import urllib.request

BASE_URL = 'http://127.0.0.1:8765'


def request(path: str, method: str = 'GET', payload: dict | None = None) -> dict:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))


def main() -> None:
    print('HEALTH', request('/health'))
    print('INIT', request('/session/init', 'POST', {'session_id': 'smoke-test'}))
    print(
        'EXEC',
        request(
            '/execute',
            'POST',
            {
                'session_id': 'smoke-test',
                'code': "import birt\nprint('birt backend ok')",
            },
        ),
    )


if __name__ == '__main__':
    main()
