import sqlite3
from datetime import datetime, timedelta

DB_PATH = "database.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_average_mood_last_7_days():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT student_id, AVG(mood_score)
        FROM mood_logs
        WHERE date >= date('now', '-7 days')
        GROUP BY student_id
    """)
    result = cur.fetchall()
    conn.close()
    return result

def detect_trend_for_student(student_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT mood_score FROM mood_logs
        WHERE student_id = ?
        ORDER BY date DESC
        LIMIT 6
    """, (student_id,))
    scores = [row[0] for row in cur.fetchall()]
    conn.close()

    if len(scores) < 6:
        return "No trend"
    prev_avg = sum(scores[3:6]) / 3
    recent_avg = sum(scores[0:3]) / 3
    if recent_avg > prev_avg + 0.5:
        return "Mood trending up"
    elif recent_avg < prev_avg - 0.5:
        return "Mood trending down"
    else:
        return "Stable"

def get_students_with_consistently_low_mood(threshold=3, days=7, occurrences=2):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT student_id, COUNT(*) as low_days
        FROM mood_logs
        WHERE mood_score <= ? AND date >= date('now', '-{days} days')
        GROUP BY student_id
        HAVING low_days >= ?
    """, (threshold, occurrences))
    result = cur.fetchall()
    conn.close()
    return result
