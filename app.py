from flask import Flask, render_template
from flask_login import LoginManager
from dotenv import load_dotenv
from datetime import datetime
from flask_dance.contrib.google import make_google_blueprint
from supabase import create_client
import os

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()

# -------------------------------
# Flask app setup
# -------------------------------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_secret_key")

# -------------------------------
# Supabase setup
# -------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# -------------------------------
# Flask-Login setup
# -------------------------------
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

# -------------------------------
# Google OAuth setup (correct redirect and prefix)
# -------------------------------
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")

google_bp = make_google_blueprint(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ],
    redirect_url="/auth/google/authorized"  # Must match your route in auth.py
)
app.register_blueprint(google_bp, url_prefix="/auth/google")

# -------------------------------
# Import Blueprints and User class
# -------------------------------
from auth import auth, users, User
from mood import mood

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

# Register Blueprints
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(mood, url_prefix="/mood")

# -------------------------------
# Context processor
# -------------------------------
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# -------------------------------
# Base routes
# -------------------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

# -------------------------------
# Run app
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)

