from flask import Flask, jsonify, request
from db import init_db, get_items, add_item, get_balance, get_balances, update_balance
import sqlite3

app = Flask(__name__)

# Ensure DB/table exists at import time
init_db()


@app.route('/api/items', methods=['GET'])
def list_items():
    rows = get_items()
    items = []
    for r in rows:
        items.append({
            'id': r['id'],
            'user_id': r['user_id'],
            'display_name': r['display_name'],
            'response': r['response'],
            'created_at': r['created_at']
        })
    return jsonify(items)


@app.route('/api/items', methods=['POST'])
def create_item():
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id')
    display_name = data.get('display_name')
    response = data.get('response')
    missing = [field for field in ['user_id', 'display_name', 'response'] if not data.get(field)]
    if missing:
        return jsonify({'error': f"Missing fields: {', '.join(missing)}"}), 400
    item_id = add_item(user_id, display_name, response)
    update_balance(user_id, display_name, 0)
    return jsonify({
        'id': item_id,
        'user_id': user_id,
        'display_name': display_name,
        'response': response,
    }), 201


@app.route('/api/balance', methods=['GET'])
def get_balance_route():
    user_id = request.args.get('user_id') or request.args.get('userID')
    if not user_id:
        return jsonify({'error': 'user_id query param required'}), 400
    row = get_balance(user_id)
    if row:
        return jsonify({
            'user_id': row['user_id'],
            'display_name': row['display_name'],
            'balance': row['balance'],
            'updated_at': row['updated_at'],
        })
    return jsonify({'error': 'not found'}), 404


@app.route('/api/balances', methods=['GET'])
def list_balances():
    rows = get_balances()
    balances = [
        {
            'user_id': r['user_id'],
            'display_name': r['display_name'],
            'balance': r['balance'],
            'updated_at': r['updated_at'],
        }
        for r in rows
    ]
    return jsonify(balances)


@app.route('/api/data', methods=['GET'])
def get_data():
    user_id = request.args.get('userID')
    if not user_id:
        return jsonify({'error': "userID query param required"}), 400
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, social_credit FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
    except Exception:
        return jsonify({'error': 'database error'}), 500
    if row:
        return jsonify({'id': row[0], 'name': row[1], 'social_credit': row[2]})
    return jsonify({'error': 'not found'}), 404


@app.route('/')
def playground():
    return '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>API Playground</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 24px; }
      textarea, input { width: 100%; box-sizing: border-box; }
      input { padding: 8px; }
      button { padding: 8px 16px; margin-top: 8px; }
      pre { background: #f4f4f4; padding: 12px; white-space: pre-wrap; word-wrap: break-word; }
      .group { margin-bottom: 24px; }
      label { display: block; margin-top: 12px; }
    </style>
  </head>
  <body>
    <h1>Flask API Playground</h1>
    <div class="group">
      <h2>GET /api/items</h2>
      <button id="get-items">Fetch Items</button>
      <pre id="get-result">Click above to fetch items.</pre>
    </div>
    <div class="group">
      <h2>POST /api/items</h2>
      <label for="post-user-id">User ID</label>
      <input id="post-user-id" type="text" placeholder="Enter user id" />
      <label for="post-display-name">Display Name</label>
      <input id="post-display-name" type="text" placeholder="Enter display name" />
      <label for="post-response">Response</label>
      <input id="post-response" type="text" placeholder="Enter response" />
      <button id="post-item">Create Item</button>
      <pre id="post-result">Enter values and click create.</pre>
    </div>
    <div class="group">
      <h2>GET /api/balance?user_id=...</h2>
      <label for="balance-user-id">User ID</label>
      <input id="balance-user-id" type="text" placeholder="Enter user id" />
      <button id="get-balance">Fetch Balance</button>
      <pre id="balance-result">Enter a user id and click fetch balance.</pre>
    </div>
    <div class="group">
      <h2>GET /api/balances</h2>
      <button id="get-balances">Fetch All Balances</button>
      <pre id="balances-result">Click to fetch all balances.</pre>
    </div>
    <script>
      async function fetchJson(url, opts) {
        const res = await fetch(url, opts);
        const text = await res.text();
        try { return JSON.parse(text); } catch { return text; }
      }
      document.getElementById('get-items').onclick = async () => {
        const result = await fetchJson('/api/items');
        document.getElementById('get-result').textContent = JSON.stringify(result, null, 2);
      };
      document.getElementById('post-item').onclick = async () => {
        const userId = document.getElementById('post-user-id').value;
        const displayName = document.getElementById('post-display-name').value;
        const responseText = document.getElementById('post-response').value;
        const result = await fetchJson('/api/items', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: userId,
            display_name: displayName,
            response: responseText,
          })
        });
        document.getElementById('post-result').textContent = JSON.stringify(result, null, 2);
      };
      document.getElementById('get-balance').onclick = async () => {
        const userId = document.getElementById('balance-user-id').value;
        const result = await fetchJson('/api/balance?user_id=' + encodeURIComponent(userId));
        document.getElementById('balance-result').textContent = JSON.stringify(result, null, 2);
      };
      document.getElementById('get-balances').onclick = async () => {
        const result = await fetchJson('/api/balances');
        document.getElementById('balances-result').textContent = JSON.stringify(result, null, 2);
      };
    </script>
  </body>
</html>
'''

print('Registered routes:', list(app.url_map.iter_rules()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
