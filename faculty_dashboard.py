from flask import Blueprint, render_template
from analytics import get_average_mood_last_7_days
from mood import get_all_moods  # Make sure this exists and returns proper data

faculty_bp = Blueprint('faculty', __name__, url_prefix='/faculty')

@faculty_bp.route('/dashboard')
def faculty_dashboard():
    all_moods = get_all_moods()
    averages = get_average_mood_last_7_days()

    return render_template('faculty_dashboard.html', all_moods=all_moods, averages=averages)
