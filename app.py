from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

people_count = 0
status = "NORMAL"
max_people = 0

@app.route("/")
def home():
    with open("data.txt", "r") as f:
        
        data = f.read().split(",")

    people_count = data[0]
    status = data[1]
    max_people = data[2]

    history_rows = ""

    with open("logs/detection_log.csv", "r") as f:
        lines = f.readlines()
        recent_logs = lines[-10:]
    
    for log in reversed(recent_logs[1:]):
        timestamp, count = log.strip().split(",")
        history_rows += f"""
        <tr>
            <td>{timestamp}</td>
            <td>{count}</td>
        </tr>
        """

    current_time = datetime.now().strftime(
        "%H:%M:%S"
    )

    if status == "NORMAL":
        status_color = "green"
    else:
        status_color = "red"

    return f"""

    <html>

    <head>
    <title>Occupancy Dashboard</title>
    <meta http-equiv="refresh" content="2">

    <style>

    body {{
        font-family: Arial;
        background-color: #f4f4f4;
        text-align: center;
    }}

    .card {{
        background: white;
        width: 300px;
        margin: 20px auto;
        padding: 20px;
        border-radius: 10px;
    }}

    .header {{
    background-color: #222;
    color: white;
    padding: 20px;
    }}

    table {{
    width: 100%;
    border-collapse: collapse;
    }}

    th, td {{
        border: 1px solid #ddd;
        padding: 8px;
    }}

    th {{
        background-color: #222;
        color: white;
    }}

    </style>
    </head>

    <body>
    <hr>
    <div class="header">
    <h1>Smart Occupancy Monitoring System</h1>
    </div>

    <p>Last Updated: {current_time}</p>

    <div class="card">
        <h2>People Count</h2>
        <h1>{people_count}</h1>
    </div>

    <div class="card">
        <h2>Status</h2>
        <h1 style="color:{status_color}">{status}</h1>
    </div>

    <div class="card">
        <h2>Max People</h2>
        <h1>{max_people}</h1>
    </div>

    <div class="card">
        <h2>Last Updated</h2>
        <h1>{current_time}</h1>
    </div>

    <div class="card">
    <h2>Recent Detection History</h2>
    <table>
    <tr>
        <th>Timestamp</th>
        <th>Count</th>
    </tr>
    {history_rows}
    </table>
    </div>

    <div class="card">
    <h2>API Endpoint</h2>
    <p><a href="/api/status">View JSON Data</a></p>
    </div>

    </body>
    </html>

    """
@app.route("/api/status")
def api_status():
    with open("data.txt", "r") as f:
        data = f.read().split(",")

    return jsonify({
        "people_count": data[0],
        "status": data[1],
        "max_people": data[2]
    })

if __name__ == "__main__":
    app.run(debug=True)