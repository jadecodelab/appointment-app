from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)
DATABASE = 'appointments.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
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
    return render_template('index.html')


@app.route('/health')
def health():
    return "OK"


@app.route('/appointments', methods=['GET'])
def get_appointments():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, date, time FROM appointments ORDER BY date, time")
    rows = cursor.fetchall()

    conn.close()

    appointments = []
    for row in rows:
        appointments.append({
            "id": row["id"],
            "name": row["name"],
            "date": row["date"],
            "time": row["time"]
        })

    return jsonify(appointments)


@app.route('/appointments', methods=['POST'])
def add_appointment():
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    date = data.get("date")
    time = data.get("time")

    if isinstance(name, str):
        name = name.strip()

    if not name or not date or not time:
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM appointments WHERE date=? AND time=?",
        (date, time)
    )
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return jsonify({"error": "Time slot already booked"}), 400

    cursor.execute(
        "INSERT INTO appointments (name, date, time) VALUES (?, ?, ?)",
        (name, date, time)
    )
    appointment_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Appointment added",
        "appointment": {
            "id": appointment_id,
            "name": name,
            "date": date,
            "time": time
        }
    }), 201


@app.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def delete_appointment_by_id(appointment_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM appointments WHERE id=?", (appointment_id,))
    existing = cursor.fetchone()

    if not existing:
        conn.close()
        return jsonify({"error": "Appointment not found"}), 404

    cursor.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Appointment deleted"}), 200


@app.route('/appointments', methods=['DELETE'])
def delete_appointment():
    data = request.get_json(silent=True) or {}

    date = data.get("date")
    time = data.get("time")

    if not date or not time:
        return jsonify({"error": "Missing date or time"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM appointments WHERE date=? AND time=?",
        (date, time)
    )
    existing = cursor.fetchone()

    if not existing:
        conn.close()
        return jsonify({"error": "Appointment not found"}), 404

    cursor.execute(
        "DELETE FROM appointments WHERE date=? AND time=?",
        (date, time)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Appointment deleted"}), 200


if __name__ == '__main__':
    init_db()
    app.run(debug=True, use_reloader=False)
