from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('appointments.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            time TEXT
        )
    ''')

    conn.commit()
    conn.close()

@app.route('/')
def home():
    return "Welcome to Appointment API!"

@app.route('/health')
def health():
    return "OK"

# ✅ GET all appointments
@app.route('/appointments', methods=['GET'])
def get_appointments():
    conn = sqlite3.connect('appointments.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name, date, time FROM appointments")
    rows = cursor.fetchall()

    conn.close()

    appointments = []
    for row in rows:
        appointments.append({
            "name": row[0],
            "date": row[1],
            "time": row[2]
        })

    return jsonify(appointments)

# ✅ POST new appointment
@app.route('/appointments', methods=['POST'])
def add_appointment():
    data = request.json

    name = data.get("name")
    date = data.get("date")
    time = data.get("time")

    if not name or not date or not time:
        return jsonify({"error": "Missing required fields"}), 400

    conn = sqlite3.connect('appointments.db')
    cursor = conn.cursor()

    # ✅ Check conflict
    cursor.execute(
        "SELECT * FROM appointments WHERE date=? AND time=?",
        (date, time)
    )
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return jsonify({"error": "Time slot already booked"}), 400

    # ✅ Insert into DB
    cursor.execute(
        "INSERT INTO appointments (name, date, time) VALUES (?, ?, ?)",
        (name, date, time)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Appointment added"}), 201

# Delete Appointment
@app.route('/appointments', methods=['DELETE'])
def delete_appointment():
    data = request.json

    date = data.get("date")
    time = data.get("time")

    if not date or not time:
        return jsonify({"error": "Missing date or time"}), 400

    conn = sqlite3.connect('appointments.db')
    cursor = conn.cursor()

    # Check if appointment exists
    cursor.execute(
        "SELECT * FROM appointments WHERE date=? AND time=?",
        (date, time)
    )
    existing = cursor.fetchone()

    if not existing:
        conn.close()
        return jsonify({"error": "Appointment not found"}), 404

    # Delete appointment
    cursor.execute(
        "DELETE FROM appointments WHERE date=? AND time=?",
        (date, time)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Appointment deleted"}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)