from flask import make_response, jsonify
from flask_restful import Resource
from config import db, app, api
from flask import request
from models import User, Cart, CartItem

# Secret key for sessions
app.config['SECRET_KEY'] = 'secret_key'

@app.route('/')
def home():
    return 'Welcome to the Home Page'

@app.route('/ci')
def ci():
    return 'Welcome to the CI/CD with Github Actions'

@app.route('/cart/<int:cart_id>', methods=['GET'])
def get_cart(cart_id):
    cart = Cart.query.get_or_404(cart_id)
    return jsonify(cart.to_dict())

if __name__ == '__main__':
    app.run(debug=True)