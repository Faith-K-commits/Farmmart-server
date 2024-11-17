import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_bcrypt import Bcrypt
load_dotenv()

app = Flask(__name__)

@app.route('/config')
def config():
    return 'This is the config route'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
migrate = Migrate(app, db)
bycrypt = Bcrypt(app)
CORS(app)
api=Api(app)
db.init_app(app)