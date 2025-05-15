from flask import Flask, render_template
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from datetime import datetime
from flask_dance.contrib.google import make_google_blueprint, google

# Load environment variables from .env (this must be called before you use os.getenv())
load_dotenv()

# Configuration class to access Supabase credentials from environment variables
class Config:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
    GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_default_dev_secret")

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
# Initialize Supabase Client (if needed later for database operations)
from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

# -------------------------------
# Google OAuth setup
# -------------------------------
google_bp = make_google_blueprint(client_id=Config.GOOGLE_OAUTH_CLIENT_ID,
                                  client_secret=Config.GOOGLE_OAUTH_CLIENT_SECRET,
                                  redirect_to="google.login")
app.register_blueprint(google_bp, url_prefix="/google_login")

# Import Blueprints and User model
from auth import auth, users, User  # Make sure your user model is imported here
from mood import mood

# Shared user_loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

# Register Blueprints
app.register_blueprint(auth, url_prefix="/auth")              # login, register, dashboard
app.register_blueprint(mood, url_prefix="/mood")              # mood logging routes

# Global context
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Basic routes
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

# Run the app
if __name__ == "__main__":
    app.run(debug=True)

