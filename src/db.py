import sqlite3

DB_PATH = 'data.db'


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(items)')
    table_info = cursor.fetchall()
    if not table_info:
        cursor.execute(
            '''CREATE TABLE items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                display_name TEXT,
                response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''
        )
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS balances (
                user_id TEXT PRIMARY KEY,
                display_name TEXT,
                balance INTEGER NOT NULL DEFAULT 100,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''
        )
        conn.commit()
        conn.close()
        return

    columns = [row[1] for row in table_info]
    if 'content' in columns:
        cursor.execute('ALTER TABLE items RENAME TO items_old')
        cursor.execute(
            '''CREATE TABLE items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                display_name TEXT,
                response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''
        )
        cursor.execute(
            'INSERT INTO items (user_id, display_name, response, created_at) '
            'SELECT NULL, NULL, content, created_at FROM items_old'
        )
        cursor.execute('DROP TABLE items_old')
    else:
        required_columns = {'user_id', 'display_name', 'response'}
        missing = required_columns - set(columns)
        for column in missing:
            cursor.execute(f'ALTER TABLE items ADD COLUMN {column} TEXT')

    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS balances (
            user_id TEXT PRIMARY KEY,
            display_name TEXT,
            balance INTEGER NOT NULL DEFAULT 100,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''
    )
    conn.commit()
    conn.close()


def add_item(user_id: str, display_name: str, response: str) -> int:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO items (user_id, display_name, response) VALUES (?, ?, ?)',
        (user_id, display_name, response),
    )
    conn.commit()
    rowid = cursor.lastrowid
    conn.close()
    return rowid


def get_items():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT id, user_id, display_name, response, created_at FROM items ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_balance(user_id: str, display_name: str, delta: int) -> int:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO balances (user_id, display_name, balance) VALUES (?, ?, ?) '
        'ON CONFLICT(user_id) DO UPDATE SET '
        'balance = balances.balance + excluded.balance, '
        'display_name = excluded.display_name, '
        'updated_at = CURRENT_TIMESTAMP',
        (user_id, display_name, delta),
    )
    conn.commit()
    cursor.execute('SELECT balance FROM balances WHERE user_id = ?', (user_id,))
    balance = cursor.fetchone()['balance']
    conn.close()
    return balance


def get_balance(user_id: str):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, display_name, balance, updated_at FROM balances WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def get_balances():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, display_name, balance, updated_at FROM balances ORDER BY user_id')
    rows = cursor.fetchall()
    conn.close()
    return rows
