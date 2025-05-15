from flask import Blueprint, redirect, url_for, render_template, flash, session, request
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import os

# -------------------------------
# Blueprints
# -------------------------------

auth = Blueprint('auth', __name__)

# Flask-Dance Google OAuth blueprint
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
    redirect_url="http://ripple.catecs.org/auth/google/authorized"
)

)

# -------------------------------
# Flask-Login setup
# -------------------------------

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(auth)

class User(UserMixin):
    def __init__(self, id, first_name=None, last_name=None, dorm=None, email=None, is_dorm_parent=False):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.dorm = dorm
        self.email = email
        self.is_dorm_parent = is_dorm_parent

# In-memory user storage (for demonstration purposes)
users = {}

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

# -------------------------------
# STUDENT Registration (no login)
# -------------------------------

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dorm = request.form.get('dorm')

        new_user = User(
            id=len(users) + 1,
            first_name=first_name,
            last_name=last_name,
            dorm=dorm,
            is_dorm_parent=False
        )
        users[new_user.id] = new_user
        session['user_id'] = new_user.id  # Student session only
        flash('Welcome to Ripple, student!')
        return redirect(url_for('mood.student_dashboard'))

    return render_template('register.html')

# -------------------------------
# DORM PARENT Login via Google
# -------------------------------

@auth.route('/login', endpoint='login')
def google_login():
    return redirect(url_for('google.login'))

@auth.route('/google/authorized')  # This must match redirect_url
def google_authorize():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info from Google.", "error")
        return redirect(url_for("auth.login"))

    user_info = resp.json()
    email = user_info.get('email', '').lower()
    first_name = user_info.get('given_name', '')
    last_name = user_info.get('family_name', '')

    # Check if dorm parent already exists
    user = next((u for u in users.values() if u.email == email and u.is_dorm_parent), None)
    if not user:
        user = User(
            id=len(users) + 1,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_dorm_parent=True
        )
        users[user.id] = user
        flash("Dorm parent account created via Google!")

    login_user(user)
    session['role'] = 'dorm_parent'
    flash("Logged in as dorm parent!")
    return redirect(url_for('auth.dashboard'))

# -------------------------------
# Dashboard (role-specific)
# -------------------------------

@auth.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_dorm_parent:
        return render_template('dashboard_faculty.html', user=current_user)
    else:
        flash("Only dorm parents can access this dashboard.")
        return redirect(url_for('auth.login'))

# -------------------------------
# Logout
# -------------------------------

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('auth.login'))
