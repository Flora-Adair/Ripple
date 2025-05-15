# register.py
import os
from flask import (
    Blueprint, redirect, url_for,
    render_template, flash, session, request
)
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, UserMixin, current_user
)

# -------------------------------
# Blueprint & OAuth setup
# -------------------------------
auth = Blueprint('auth', __name__)

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    raise ValueError("Google OAuth credentials not set!")

google_bp = make_google_blueprint(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ],
    redirect_url="/auth/google/authorized"
)

# -------------------------------
# Flask-Login setup
# -------------------------------
login_manager = LoginManager()
login_manager.login_view = "auth.login"

class User(UserMixin):
    def __init__(self, id, first_name, last_name, dorm=None, email=None, is_dorm_parent=False):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.dorm = dorm
        self.email = email
        self.is_dorm_parent = is_dorm_parent

# In-memory user store
users = {}

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

# -------------------------------
# STUDENT Registration (no OAuth)
# -------------------------------
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name  = request.form.get('last_name')
        dorm       = request.form.get('dorm')

        if not first_name or not last_name or not dorm:
            flash('Please fill in all the fields.', 'warning')
            return redirect(url_for('auth.register'))

        # Create & store
        new_user = User(
            id=len(users) + 1,
            first_name=first_name,
            last_name=last_name,
            dorm=dorm,
            is_dorm_parent=False
        )
        users[new_user.id] = new_user

        # **Auto‑log the student in**
        login_user(new_user)
        session['role'] = 'student'
        flash(f'Welcome, {new_user.first_name}!', 'success')
        return redirect(url_for('mood.student_dashboard'))

    return render_template('register.html')

# -------------------------------
# DORM PARENT Login via Google
# -------------------------------
@auth.route('/login', endpoint='login')
def login():
    return redirect(url_for('google.login'))

@auth.route('/google/authorized')
def google_authorize():
    if not google.authorized:
        return redirect(url_for('auth.login'))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info from Google.", "error")
        return redirect(url_for('auth.login'))

    info = resp.json()
    email      = info.get('email').lower()
    first_name = info.get('given_name', '')
    last_name  = info.get('family_name', '')

    # Find or create dorm parent
    user = next((u for u in users.values()
                 if u.email == email and u.is_dorm_parent), None)

    if not user:
        user = User(
            id=len(users) + 1,
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_dorm_parent=True
        )
        users[user.id] = user
        flash("Dorm parent account created via Google!", 'success')

    login_user(user)
    session['role'] = 'dorm_parent'
    flash(f"Welcome back, {user.first_name}!", 'success')
    return redirect(url_for('auth.dashboard'))

# -------------------------------
# SHARED Dashboard
# -------------------------------
@auth.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_dorm_parent:
        # Dorm parent sees faculty dashboard
        return render_template('dashboard_faculty.html', user=current_user)
    else:
        # Student sees student dashboard
        return redirect(url_for('mood.student_dashboard'))

# -------------------------------
# Logout
# -------------------------------
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.", 'info')
    return redirect(url_for('auth.login'))
