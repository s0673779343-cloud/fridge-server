from flask import Flask, request, jsonify
import sqlite3
import time

app = Flask(__name__)

DB_NAME = "fridge.db"

# =====================================================
# INIT DATABASE
# =====================================================

def init_db():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp INTEGER,
            device TEXT,

            t1 REAL,
            t2 REAL,
            t3 REAL,
            t4 REAL,

            u REAL,
            p REAL,

            power INTEGER
        )
    """)

    conn.commit()

    conn.close()

# =====================================================
# SAVE LOG
# =====================================================

def save_log(data):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO logs (

            timestamp,
            device,

            t1,
            t2,
            t3,
            t4,

            u,
            p,

            power

        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        data.get("timestamp", int(time.time())),
        data.get("device", "unknown"),

        data.get("t1", 0),
        data.get("t2", 0),
        data.get("t3", 0),
        data.get("t4", 0),

        data.get("u", 0),
        data.get("p", 0),

        data.get("power", 0)
    ))

    conn.commit()

    conn.close()

# =====================================================
# API
# =====================================================

@app.route("/api/data", methods=["POST"])
def api_data():

    data = request.json

    print(data)

    save_log(data)

    return jsonify({
        "status": "saved"
    })

# =====================================================
# TEST
# =====================================================

@app.route("/")
def home():

    return "Fridge Logger Server OK"

# =====================================================
# START
# =====================================================

init_db()

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=10000)
