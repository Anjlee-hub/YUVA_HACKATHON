import sqlite3
import os
import json
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "factory_intelligence.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Machine telemetry history (30 days)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetry_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        machine_id TEXT,
        power_kw REAL,
        energy_kwh REAL,
        runtime_hrs REAL,
        idle_time_hrs REAL,
        temperature_c REAL,
        vibration_mms REAL,
        pressure_bar REAL,
        production_units REAL,
        actual_sec REAL,
        expected_sec REAL,
        sec_deviation_pct REAL,
        is_anomaly INTEGER DEFAULT 0
    )
    """)
    
    # Factory state / settings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS factory_config (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # Verified savings registry
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS verified_savings (
        id TEXT PRIMARY KEY,
        action_title TEXT,
        machine_name TEXT,
        implemented_date TEXT,
        predicted_sec_improvement_pct REAL,
        actual_sec_improvement_pct REAL,
        kwh_saved_monthly REAL,
        inr_saved_monthly REAL,
        co2_avoided_kg_monthly REAL,
        production_impact_pct REAL,
        quality_impact_pct REAL,
        variance_explanation TEXT,
        verification_methodology TEXT
    )
    """)

    # Action execution log (audit trail of human approvals and simulations)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        event_type TEXT,
        action_id TEXT,
        title TEXT,
        actor TEXT,
        details TEXT
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized at", DB_PATH)
