"""
Minimal lab data dashboard with separated frontend assets.
Run: py labmateds.py
Requires: flask, requests, mysql-connector-python
"""

import os
import sys
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import mysql.connector
import requests
from flask import Flask, jsonify, render_template, request
from mysql.connector.connection import MySQLConnection


API_URL = "http://192.168.0.252:8000/reportapi/LabmatePatRegistration.svc/Getpatientdatabymobileno"

DB_CONFIG = {
    "host": os.getenv("LABMATE_DB_HOST", "localhost"),
    "user": os.getenv("LABMATE_DB_USER", "root"),
    "password": os.getenv("LABMATE_DB_PASS", ""),
    "database": "Labmate_data_structure",
}


CENTER_MAP = {
    "10": "center10",
    "11": "center11",
    "13": "center13",
    "15": "center15",
    "19": "center19",
}

CENTER_DEFAULT_START = {
    "10": 102564600,
    "11": 11252305,
    "13": 13257386,
    "15": 152563097,
    "19": 19251560,
}

app = Flask(__name__, static_folder="static", template_folder="templates")
_scheduler_lock = threading.Lock()


# --- DB helpers ------------------------------------------------------------ #
def db_root_connection() -> MySQLConnection:
    return mysql.connector.connect(
        host=DB_CONFIG["host"], user=DB_CONFIG["user"], password=DB_CONFIG["password"]
    )


def db_connection() -> MySQLConnection:
    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
    )


def ensure_database_and_tables() -> None:
    # Create database if missing.
    with db_root_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`;")
        cur.close()

    schema = """
    CREATE TABLE IF NOT EXISTS `{table}` (
        patientid BIGINT PRIMARY KEY,
        patientname VARCHAR(120),
        mobileno VARCHAR(20),
        age VARCHAR(32),
        bdate VARCHAR(32),
        gender VARCHAR(16),
        address TEXT,
        doctor VARCHAR(120),
        doctormobile VARCHAR(32),
        panel VARCHAR(64),
        ordertest TEXT,
        reportstatus VARCHAR(32),
        pdffile VARCHAR(255),
        whatsapp VARCHAR(32),
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    with db_connection() as conn:
        cur = conn.cursor()
        for tbl in CENTER_MAP.values():
            cur.execute(schema.replace("{table}", tbl))
        conn.commit()
        cur.close()


def center_from_patientid(pid: str) -> str:
    if len(pid) < 2:
        return ""
    return CENTER_MAP.get(pid[:2], "")


def get_center_min_max(table: str) -> Dict[str, Optional[int]]:
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT MIN(patientid), MAX(patientid) FROM `{table}`;")
        row = cur.fetchone() or (None, None)
        cur.close()
    return {"min": row[0], "max": row[1]}


def fetch_patient_from_api(patientid: str) -> Dict[str, Any]:
    payload = {"mobileno": "", "patientid": int(patientid)}
    resp = requests.post(API_URL, json=payload, timeout=10)
    resp.raise_for_status()
    body = resp.json()
    data = body.get("data") or []
    return data[0] if data else {}


def upsert_patient(table: str, record: Dict[str, Any]) -> None:
    insert_sql = f"""
        INSERT INTO `{table}` (
            patientid, patientname, mobileno, age, bdate, gender, address,
            doctor, doctormobile, panel, ordertest, reportstatus, pdffile,
            whatsapp, message
        )
        VALUES (%(patientid)s, %(patientname)s, %(mobileno)s, %(age)s, %(bdate)s,
                %(gender)s, %(address)s, %(doctor)s, %(doctormobile)s, %(panel)s,
                %(ordertest)s, %(reportstatus)s, %(pdffile)s, %(whatsapp)s, %(message)s)
        ON DUPLICATE KEY UPDATE
            patientname=VALUES(patientname),
            mobileno=VALUES(mobileno),
            age=VALUES(age),
            bdate=VALUES(bdate),
            gender=VALUES(gender),
            address=VALUES(address),
            doctor=VALUES(doctor),
            doctormobile=VALUES(doctormobile),
            panel=VALUES(panel),
            ordertest=VALUES(ordertest),
            reportstatus=VALUES(reportstatus),
            pdffile=VALUES(pdffile),
            whatsapp=VALUES(whatsapp),
            message=VALUES(message);
    """
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute(insert_sql, record)
        conn.commit()
        cur.close()


# --- Routes ---------------------------------------------------------------- #
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/api/fetch-patient", methods=["POST"])
def api_fetch_patient():
    body = request.get_json(force=True)
    patientid = str(body.get("patientid", "")).strip()
    if not patientid.isdigit():
        return jsonify({"ok": False, "error": "Patient ID must be numeric."}), 400

    table = center_from_patientid(patientid)
    if not table:
        return jsonify({"ok": False, "error": "Patient ID prefix does not map to a center."}), 400

    if table not in CENTER_MAP.values():
        return jsonify({"ok": False, "error": "Unknown center."}), 400

    bounds = get_center_min_max(table)
    default_start = CENTER_DEFAULT_START.get(patientid[:2])
    if default_start is None:
        return jsonify({"ok": False, "error": "No default start ID configured for this center."}), 400

    if bounds["max"] is None:
        if int(patientid) != int(default_start):
            msg = (
                f"Your DB entries start from patient ID {default_start}. "
                f"Please enter {default_start} to avoid database mismatch."
            )
            return jsonify({"ok": False, "error": msg}), 409
    else:
        expected_next = int(bounds["max"]) + 1
        if int(patientid) < int(bounds["min"] or expected_next):
            msg = (
                f"Your DB entries start from patient ID {bounds['min']}. "
                "You cannot fetch previous IDs because it will mismatch the database."
            )
            return jsonify({"ok": False, "error": msg}), 409
        if int(patientid) != expected_next:
            msg = (
                f"Last saved patient ID is {bounds['max']}. "
                f"Please enter {expected_next} to continue, otherwise the database will mismatch."
            )
            return jsonify({"ok": False, "error": msg}), 409

    try:
        record = fetch_patient_from_api(patientid)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"ok": False, "error": f"API error: {exc}"}), 502

    if not record:
        return jsonify({"ok": False, "error": "No record returned for this ID."}), 404

    record_pid = record.get("patientid", "")
    record_pid = "" if record_pid is None else str(record_pid).strip()
    if record_pid == "" or record_pid == "0" or record_pid.lower() == "null":
        return jsonify({"ok": False, "error": "No record returned for this ID."}), 404

    record["patientid"] = int(record_pid or patientid)
    try:
        upsert_patient(table, record)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"ok": False, "error": f"DB error: {exc}"}), 500

    return jsonify({"ok": True, "table": table, "saved": record})


@app.route("/api/center/<center>", methods=["GET"])
def api_center(center: str):
    table = CENTER_MAP.get(center)
    if not table:
        return jsonify({"ok": False, "error": "Unknown center."}), 400

    with db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(f"SELECT * FROM `{table}` ORDER BY patientid DESC;")
        rows = cur.fetchall()
        cur.close()
    return jsonify({"ok": True, "rows": rows})


def _scheduler_interval_seconds(now: time.struct_time) -> int:
    hour = now.tm_hour
    if 8 <= hour < 22:
        return 30 * 60
    return 60 * 60


def _run_center_cycle(center: str) -> None:
    table = CENTER_MAP[center]
    bounds = get_center_min_max(table)
    start_id = bounds["max"] + 1 if bounds["max"] is not None else CENTER_DEFAULT_START[center]
    current_id = int(start_id)

    print(f"[scheduler] fetching center {center} from {current_id}")
    while True:
        try:
            record = fetch_patient_from_api(str(current_id))
        except Exception:
            time.sleep(3)
            continue

        if not record:
            break

        record_pid = record.get("patientid", "")
        record_pid = "" if record_pid is None else str(record_pid).strip()
        if record_pid == "" or record_pid == "0" or record_pid.lower() == "null":
            break

        record["patientid"] = int(record_pid or current_id)
        try:
            upsert_patient(table, record)
        except Exception:
            time.sleep(3)
            continue

        current_id += 1
    print(f"[scheduler] center {center} completed at {current_id - 1}")


def scheduler_loop() -> None:
    while True:
        with _scheduler_lock:
            for center in ["10", "11", "13", "15", "19"]:
                _run_center_cycle(center)
        interval = _scheduler_interval_seconds(time.localtime())
        next_run = datetime.now() + timedelta(seconds=interval)
        print(f"[scheduler] all centers completed. Next run at {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(interval)


def start_scheduler_thread() -> None:
    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()


if __name__ == "__main__":
    try:
        ensure_database_and_tables()
    except Exception as exc:  # noqa: BLE001
        print(f"[fatal] Could not set up database: {exc}")
        sys.exit(1)

    start_scheduler_thread()
    port = int(os.getenv("PORT", "3005"))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
