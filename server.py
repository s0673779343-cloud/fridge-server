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
# HOME
# =====================================================

@app.route("/")
def home():

    return "Fridge Logger Server OK"

# =====================================================
# LOGS PAGE
# =====================================================

@app.route("/logs")
def logs():

    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM logs
        ORDER BY id DESC
        LIMIT 100
    """)

    rows = cursor.fetchall()

    conn.close()

    html = """

    <html>

    <head>

        <title>Fridge Logs</title>

        <meta http-equiv="refresh" content="10">

        <style>

            body {
                font-family: Arial;
                background: #111;
                color: #eee;
                padding: 20px;
            }

            table {
                border-collapse: collapse;
                width: 100%;
            }

            td, th {
                border: 1px solid #444;
                padding: 8px;
                text-align: center;
            }

            th {
                background: #222;
            }

        </style>

    </head>

    <body>

    <h2>Логер холодильника</h2>

    <table>

    <tr>
        <th>ID</th>
        <th>TIME</th>
        <th>T1</th>
        <th>T2</th>
        <th>T3</th>
        <th>T4</th>
        <th>POWER</th>
    </tr>

    """

    for row in rows:

        html += f"""

        <tr>

            <td>{row['id']}</td>

            <td>
                {time.strftime('%H:%M:%S',
                time.gmtime(row["timestamp"] + 3 * 3600))}
            </td>

            <td>{row['t1']}</td>
            <td>{row['t2']}</td>
            <td>{row['t3']}</td>
            <td>{row['t4']}</td>

            <td>{row['power']}</td>

        </tr>

        """

    html += """

    </table>

    </body>

    </html>

    """

    return html

# =====================================================
# CHART DATA
# =====================================================

@app.route("/chart-data")
def chart_data():

    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *
        FROM logs

        ORDER BY id DESC

        LIMIT 50

    """)

    rows = cursor.fetchall()

    conn.close()

    data = []

    for row in reversed(rows):

        data.append({

"time": time.strftime(
    '%H:%M:%S',
    time.gmtime(row["timestamp"] + 3 * 3600)
),
            "t1": row["t1"],
            "t2": row["t2"],
            "t3": row["t3"],
            "t4": row["t4"]
        })

    return jsonify(data)

# =====================================================
# CHART PAGE
# =====================================================

@app.route("/chart")
def chart():

    return """

    <html>

    <head>

        <title>Fridge Charts</title>

        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

        <meta http-equiv="refresh" content="60">

        <style>

            body {
                background: #111;
                color: white;
                font-family: Arial;
                padding: 20px;
            }

            canvas {
                background: #222;
                border-radius: 10px;
                padding: 10px;
            }

        </style>

    </head>

    <body>

        <h2>Графіки температури холодильника</h2>

        <canvas id="tempChart"></canvas>

        <script>

        async function loadData() {

            const response = await fetch('/chart-data');

            const data = await response.json();

            const labels = data.map(x => x.time);

            const t1 = data.map(x => x.t1);
            const t2 = data.map(x => x.t2);
            const t3 = data.map(x => x.t3);
            const t4 = data.map(x => x.t4);

            new Chart(document.getElementById('tempChart'), {

                type: 'line',

                data: {

                    labels: labels,

                    datasets: [

                        {
                            label: 'T1',
                            data: t1,
                            borderColor: 'red'
                        },

                        {
                            label: 'T2',
                            data: t2,
                            borderColor: 'green'
                        },

                        {
                            label: 'T3',
                            data: t3,
                            borderColor: 'blue'
                        },

                        {
                            label: 'T4',
                            data: t4,
                            borderColor: 'yellow'
                        }

                    ]
                },

                options: {

                    responsive: true,

                    scales: {

                        y: {
                            beginAtZero: false
                        }
                    }
                }
            });
        }

        loadData();

        </script>

    </body>

    </html>

    """

# =====================================================
# START
# =====================================================

init_db()

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=10000)
