import sqlite3

DB_PATH = "mood.db"  # same as your mood.py

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_average_mood_last_7_days():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, AVG(mood_score) AS avg_mood
        FROM moods
        WHERE DATE(timestamp) >= DATE('now', '-7 days')
        GROUP BY user_id
    """)
    result = cur.fetchall()
    conn.close()
    return result

def detect_trend_for_student(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT mood_score FROM moods
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 6
    """, (user_id,))
    scores = [row['mood_score'] for row in cur.fetchall()]
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
    cur.execute("""
        SELECT user_id, COUNT(*) as low_days
        FROM moods
        WHERE mood_score <= ? AND DATE(timestamp) >= DATE('now', ?)
        GROUP BY user_id
        HAVING low_days >= ?
    """, (threshold, f'-{days} days', occurrences))
    result = cur.fetchall()
    conn.close()
    return result

