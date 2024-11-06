from flask import make_response, jsonify
from flask_restful import Resource
from config import db, app, api

# Secret key for sessions
app.config['SECRET_KEY'] = 'secret_key'

@app.route('/')
def home():
    return 'Welcome to the Home Page'

if __name__ == '__main__':
    app.run(debug=True)