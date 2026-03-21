import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

DB_PATH = "data/analysis_history.db"

def init_sqlite_db():
    """Initialize the SQLite database with the requested O*NET schema."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        match_score FLOAT,
        matched_skills TEXT, -- Store as JSON string
        missing_skills TEXT, -- Store as JSON string
        roadmap_json TEXT    -- Store full steps as JSON
    );
    """)
    conn.commit()
    conn.close()

def save_analysis_history(user_id: str, match_score: float, matched_skills: List[str], missing_skills: List[str], roadmap: List[Dict]):
    """Save an analysis result to the SQLite history."""
    init_sqlite_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO analysis_history (user_id, match_score, matched_skills, missing_skills, roadmap_json)
    VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        match_score,
        json.dumps(matched_skills),
        json.dumps(missing_skills),
        json.dumps(roadmap)
    ))
    conn.commit()
    conn.close()

def get_analysis_history(user_id: str) -> List[Dict]:
    """Retrieve history for a user."""
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis_history WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "id": row["id"],
            "timestamp": row["timestamp"],
            "match_score": row["match_score"],
            "matched_skills": json.loads(row["matched_skills"]),
            "missing_skills": json.loads(row["missing_skills"]),
            "roadmap": json.loads(row["roadmap_json"])
        })
    return results
