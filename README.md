# Appointment Assistant API

##  Overview

A RESTful backend API for managing appointment scheduling with conflict detection and persistent storage.

## Features

* Create appointments (POST)
* View all appointments (GET)
* Delete appointments (DELETE)
* Prevent double booking (same date & time)
* Input validation and error handling
* SQLite database for persistent storage

## Tech Stack

* Python
* Flask
* SQLite

## How to Run

```bash
python app.py
```

## API Endpoints

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

## Future Improvements

* Add authentication (login system)
* Connect to frontend UI
* Integrate with voice assistant system
