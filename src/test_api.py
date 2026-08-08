import json
import urllib.request

BASE = 'http://127.0.0.1:5000'

def post_item(user_id, display_name, response):
    url = f"{BASE}/api/items"
    data = json.dumps({
        'user_id': user_id,
        'display_name': display_name,
        'response': response,
    }).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        print('POST:', resp.read().decode())


def get_items():
    url = f"{BASE}/api/items"
    with urllib.request.urlopen(url) as resp:
        print('GET:', resp.read().decode())


if __name__ == '__main__':
    post_item('U080Y31KUE7', 'Skylar', 'Oh')
    get_items()
