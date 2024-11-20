import os
from dotenv import load_dotenv
from flask import Flask, current_app
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_bcrypt import Bcrypt
import cloudinary
from flask_login import LoginManager

load_dotenv()

app = Flask(__name__)

@app.route('/config')
def config():
    return 'This is the config route'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'

db = SQLAlchemy()
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
CORS(app)
api=Api(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load the user from the database for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    with current_app.app_context():
        from models import BaseUser
        return BaseUser.query.get(user_id)

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)
