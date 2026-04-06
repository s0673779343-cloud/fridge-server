from flask import Flask, request
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS temps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device TEXT,
            timestamp INTEGER,
            t1 REAL,
            t2 REAL,
            t3 REAL,
            t4 REAL,
            u REAL,
            p REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return "Server is running"

@app.route('/api/data', methods=['POST'])
def receive():
    data = request.json

    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute('''
        INSERT INTO temps (device, timestamp, t1, t2, t3, t4, u, p)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('device'),
        data.get('timestamp'),
        data.get('t1'),
        data.get('t2'),
        data.get('t3'),
        data.get('t4'),
        data.get('u'),
        data.get('p')
    ))

    conn.commit()
    conn.close()

    return {"status": "ok"}
