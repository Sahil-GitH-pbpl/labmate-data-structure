# ARPRA – VoC Feedback Management System

A FastAPI + MySQL application for managing patient feedback, campaigns, and complaint workflows for Dr Bhasin's Lab.

## Project Structure
```
backend/
  Dockerfile
  requirements.txt
  app/
    main.py
    config.py
    database.py
    utils.py
    models/
    routers/
    services/
    templates/
    static/
```

## Running locally (without Docker)
1. Create and activate a virtualenv.
2. Install dependencies: `pip install -r backend/requirements.txt`.
3. Export a `DATABASE_URL` (e.g., `export DATABASE_URL=mysql+pymysql://arpra:arpra@localhost:3306/arpra_voc`).
4. Start the app: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` from the `backend` folder.

## Running with Docker
```
docker compose up --build
```
The app will be available at http://localhost:8000 and connects to the bundled MySQL service.

## Initial admin
Insert a user directly into MySQL (example SQL):
```
INSERT INTO users (name, email, role, username, password_hash)
VALUES ('Administrator', 'admin@example.com', 'admin', 'admin', SHA2('admin',256));
```
Adjust password/fields as needed.
