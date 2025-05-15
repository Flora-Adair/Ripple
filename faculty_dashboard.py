from flask import Blueprint, render_template
from analytics import get_average_mood_last_7_days, detect_trend_for_student
from mood import get_all_moods  # assuming you have this function in mood.py

faculty_bp = Blueprint('faculty', __name__, url_prefix='/faculty')

@faculty_bp.route('/dashboard')
def faculty_dashboard():
    all_moods = get_all_moods()
    averages = get_average_mood_last_7_days()
    # Optional: remove hardcoded student
    # trend = detect_trend_for_student("alexj")

    return render_template('faculty_dashboard.html', all_moods=all_moods, averages=averages)
