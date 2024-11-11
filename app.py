from flask import make_response, jsonify
from flask_restful import Resource
from config import db, app, api
from models import Vendor


# Secret key for sessions
app.config['SECRET_KEY'] = 'secret_key'

@app.route('/')
def home():
    return 'Welcome to the Home Page'

@app.route('/ci')
def ci():
    return 'Welcome to the CI/CD with Github Actions'

if __name__ == '__main__':
    app.run(debug=True)