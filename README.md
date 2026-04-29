# Appointment Assistant API

##  Overview

A RESTful backend API for managing appointment scheduling with conflict detection and persistent storage.

## Features

* Create appointments (POST)
* View all appointments (GET)
* Delete appointments (DELETE)
* Browser UI for booking and managing appointments
* Prevent double booking (same date & time)
* Input validation and error handling
* SQLite database for persistent storage

## Tech Stack

* Python
* Flask
* SQLite
* HTML/CSS/JavaScript

## How to Run

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## API Endpoints

The browser UI is served from `/`.

### GET /appointments

Returns all appointments

### POST /appointments

Create a new appointment

```json
{
  "name": "Jade",
  "date": "2026-04-20",
  "time": "10:00"
}
```

### DELETE /appointments

Delete an appointment

```json
{
  "date": "2026-04-20",
  "time": "10:00"
}
```

### DELETE /appointments/&lt;id&gt;

Delete an appointment by ID.

## Future Improvements

* Add authentication (login system)
* Integrate with voice assistant system
