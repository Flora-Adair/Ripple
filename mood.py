from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from datetime import datetime
import sqlite3

# Initialize Blueprint
mood = Blueprint('mood', __name__)

# Path to SQLite database
DATABASE = 'mood.db'


# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Initialize the database (create tables and seed data)
def init_db():
    with get_db_connection() as conn:
        conn.execute('PRAGMA foreign_keys = ON;')

        conn.execute('DROP TABLE IF EXISTS moods')
        conn.execute('DROP TABLE IF EXISTS users')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                is_dorm_parent BOOLEAN NOT NULL DEFAULT 0
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS moods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mood_score INTEGER NOT NULL,
                mood_description TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        conn.executemany('''
            INSERT OR IGNORE INTO users (id, first_name, last_name, is_dorm_parent)
            VALUES (?, ?, ?, ?)
        ''', [
            (1, 'Dorm', 'Parent', 1),
            (2, 'Student', 'A', 0),
            (3, 'Student', 'B', 0)
        ])

        print("Database initialized successfully!")


init_db()


# Helper function to get the current user from the session
def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        with get_db_connection() as conn:
            return conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    return None


# Public helper to fetch all moods (used in faculty dashboard)
def get_all_moods():
    with get_db_connection() as conn:
        rows = conn.execute('''
            SELECT moods.id, moods.mood_score, moods.mood_description, moods.timestamp,
                   users.first_name || ' ' || users.last_name AS student_name
            FROM moods
            JOIN users ON moods.user_id = users.id
            ORDER BY moods.timestamp DESC
        ''').fetchall()

    # Convert sqlite3.Row objects to dicts
    return [dict(row) for row in rows]


# Route for mood input
@mood.route('/mood_input', methods=['GET', 'POST'])
def mood_input():
    current_user = get_current_user()

    if not current_user:
        flash('You must be logged in to log a mood.')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        try:
            mood_score = int(request.form.get('mood_score'))
        except (ValueError, TypeError):
            flash('Invalid mood score. Please enter a number between 1 and 10.')
            return redirect(url_for('mood.mood_input'))

        if not (1 <= mood_score <= 10):
            flash('Mood score must be between 1 and 10.')
            return redirect(url_for('mood.mood_input'))

        mood_description = request.form.get('mood_description', '').strip()

        with get_db_connection() as conn:
            conn.execute('''
                INSERT INTO moods (user_id, mood_score, mood_description)
                VALUES (?, ?, ?)
            ''', (current_user['id'], mood_score, mood_description))

        flash('Your mood has been logged successfully!')
        return redirect(url_for('mood.student_dashboard'))

    return render_template('mood_input.html')


# Route for updating mood
@mood.route('/update_mood', methods=['GET', 'POST'])
def update_mood():
    current_user = get_current_user()

    if not current_user:
        flash('You must be logged in to update your mood.')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        try:
            mood_score = int(request.form.get('mood_score'))
        except (ValueError, TypeError):
            flash('Invalid mood score. Please enter a number between 1 and 10.')
            return redirect(url_for('mood.update_mood'))

        if not (1 <= mood_score <= 10):
            flash('Mood score must be between 1 and 10.')
            return redirect(url_for('mood.update_mood'))

        mood_description = request.form.get('mood_description', '').strip()
        today = datetime.utcnow().date()

        with get_db_connection() as conn:
            existing_mood = conn.execute('''
                SELECT * FROM moods WHERE user_id = ? AND DATE(timestamp) = ?
            ''', (current_user['id'], today)).fetchone()

            if existing_mood:
                conn.execute('''
                    UPDATE moods SET mood_score = ?, mood_description = ?
                    WHERE id = ?
                ''', (mood_score, mood_description, existing_mood['id']))
                flash('Your mood entry has been updated successfully!')
            else:
                conn.execute('''
                    INSERT INTO moods (user_id, mood_score, mood_description)
                    VALUES (?, ?, ?)
                ''', (current_user['id'], mood_score, mood_description))
                flash('A new mood entry has been created!')

        return redirect(url_for('mood.student_dashboard'))

    return render_template('mood_input.html')


# Route for the student's dashboard
@mood.route('/student_dashboard')
def student_dashboard():
    current_user = get_current_user()

    if not current_user:
        flash('You must be logged in to view your mood history.')
        return redirect(url_for('auth.login'))

    with get_db_connection() as conn:
        student_moods = conn.execute('''
            SELECT * FROM moods WHERE user_id = ? ORDER BY timestamp DESC
        ''', (current_user['id'],)).fetchall()

    return render_template('student_dashboard.html', student_moods=student_moods, current_user=current_user)


# Route for logging out (clear session)
@mood.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))
