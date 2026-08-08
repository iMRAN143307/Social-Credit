from flask import Flask, jsonify, request
import sqlite3

table = []

with sqlite3.connect("data.db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, social_credit FROM users")
    rows = cursor.fetchall()
    for row in rows:
        table.append(row)

app = Flask(__name__)

@app.route('/api/data', methods=['GET'])
def get_data():

    id = request.args.get('userID')

    for person in table:
        if person[0] == id:
            return jsonify({"name": person[1], "social_credit": person[2]})
    return jsonify({"name": "error", "social_credit": "error"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
