from datetime import datetime
from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)
DATABASE = 'appointments.db'

SERVICES = [
    "Primary Care Visit",
    "Annual Wellness Exam",
    "Sick Visit",
    "Pediatric Checkup",
    "Vaccination Appointment",
    "Lab Results Review",
    "Follow-Up Visit",
]

WEEKDAY_SLOTS = [
    "08:00", "08:30", "09:00", "09:30",
    "10:00", "10:30", "11:00", "11:30",
    "12:00", "12:30", "13:00", "13:30",
    "14:00", "14:30", "15:00", "15:30",
    "16:00", "16:30",
]

SATURDAY_SLOTS = [
    "09:00", "09:30", "10:00", "10:30",
    "11:00", "11:30", "12:00", "12:30",
]


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
            phone TEXT,
            email TEXT,
            service TEXT,
            reason TEXT,
            date TEXT,
            time TEXT
        )
    ''')

    cursor.execute("PRAGMA table_info(appointments)")
    existing_columns = {row["name"] for row in cursor.fetchall()}
    required_columns = {
        "phone": "TEXT DEFAULT ''",
        "email": "TEXT DEFAULT ''",
        "service": "TEXT DEFAULT ''",
        "reason": "TEXT DEFAULT ''",
    }

    for column_name, column_definition in required_columns.items():
        if column_name not in existing_columns:
            cursor.execute(
                f"ALTER TABLE appointments ADD COLUMN {column_name} {column_definition}"
            )

    conn.commit()
    conn.close()


def parse_appointment_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def available_slots_for_date(date_value):
    appointment_date = parse_appointment_date(date_value)

    if not appointment_date:
        return []

    weekday = appointment_date.weekday()

    if weekday < 5:
        return WEEKDAY_SLOTS

    if weekday == 5:
        return SATURDAY_SLOTS

    return []


def clean_text(value):
    if not isinstance(value, str):
        return ""

    return value.strip()


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

    cursor.execute(
        """
        SELECT id, name, phone, email, service, reason, date, time
        FROM appointments
        ORDER BY date, time
        """
    )
    rows = cursor.fetchall()

    conn.close()

    appointments = []
    for row in rows:
        appointments.append({
            "id": row["id"],
            "name": row["name"],
            "phone": row["phone"] or "",
            "email": row["email"] or "",
            "service": row["service"] or "Appointment",
            "reason": row["reason"] or "",
            "date": row["date"],
            "time": row["time"]
        })

    return jsonify(appointments)


@app.route('/appointments', methods=['POST'])
def add_appointment():
    data = request.get_json(silent=True) or {}

    name = clean_text(data.get("name"))
    phone = clean_text(data.get("phone"))
    email = clean_text(data.get("email"))
    service = clean_text(data.get("service"))
    reason = clean_text(data.get("reason"))
    date = clean_text(data.get("date"))
    time = clean_text(data.get("time"))

    if not all([name, phone, email, service, date, time]):
        return jsonify({"error": "Missing required fields"}), 400

    if service not in SERVICES:
        return jsonify({"error": "Please choose a valid service"}), 400

    available_slots = available_slots_for_date(date)

    if not available_slots:
        return jsonify({"error": "The clinic is closed on that date"}), 400

    if time not in available_slots:
        return jsonify({"error": "Please choose an available clinic time"}), 400

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
        """
        INSERT INTO appointments (name, phone, email, service, reason, date, time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (name, phone, email, service, reason, date, time)
    )
    appointment_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Appointment added",
        "appointment": {
            "id": appointment_id,
            "name": name,
            "phone": phone,
            "email": email,
            "service": service,
            "reason": reason,
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

    date = clean_text(data.get("date"))
    time = clean_text(data.get("time"))

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
    app.run(debug=False, use_reloader=False)
