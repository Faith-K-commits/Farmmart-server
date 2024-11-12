from flask import make_response, jsonify, request
from flask_restful import Resource
from config import db, app, api
from models import Animal, Orders
import cloudinary.uploader

# Secret key for sessions
app.config['SECRET_KEY'] = 'secret_key'

@app.route('/')
def home():
    return 'Welcome to the Home Page'

@app.route('/ci')
def ci():
    return 'Welcome to the CI/CD with Github Actions'

# Resource for uploading images to Cloudinary (Testing if cloudinary is available and functioning properly)
class UploadImage(Resource):
    def post(self):
        # Check if a file part is in the request
        if 'file' not in request.files:
            return {"error": "No file part in the request"}, 400

        file = request.files['file']

        # Ensure the file is not empty
        if file.filename == '':
            return {"error": "No file selected for uploading"}, 400

        try:
            # Upload the file to Cloudinary and retrieve the result
            result = cloudinary.uploader.upload(file)
            # Return the URL of the uploaded image as JSON
            return {"url": result['secure_url']}, 200
        except Exception as e:
            # Handle any exceptions and return an error message
            return {"error": str(e)}, 500

class OrdersResource(Resource):
    def get(self, order_id=None):
        if order_id:
            order = Orders.query.get_or_404(order_id)
            order_data = {
                'id': order.id,
                'user_id': order.user_id,
                'status': order.status,
                'total_price': order.calculate_total_price(),
                'created_at': order.created_at,
                'updated_at': order.updated_at
            }
            return make_response(jsonify(order_data), 200)
        else:
            orders = Orders.query.all()
            orders_data = [{
                'id': order.id,
                'user_id': order.user_id,
                'status': order.status,
                'total_price': order.calculate_total_price(),
                'created_at': order.created_at,
                'updated_at': order.updated_at
            } for order in orders]
            return make_response(jsonify(orders_data), 200)

    def post(self):
        data = request.get_json()
        
        # Validate status
        if data.get('status') not in ['Pending', 'Completed', 'Failed']:
            return {'error': 'Invalid order status'}, 400
        
        # Calculate total price before creating the order
        order = Orders(user_id=data['user_id'], status=data['status'])
        db.session.add(order)
        db.session.commit()

        return make_response(jsonify({'message': 'Order created successfully', 'id': order.id}), 201)

    def put(self, order_id):
        data = request.get_json()
        order = Orders.query.get_or_404(order_id)

        # Validate and update the status
        if data.get('status') not in ['Pending', 'Completed', 'Failed']:
            return {'error': 'Invalid order status'}, 400

        order.status = data.get('status', order.status)
        order.total_price = order.calculate_total_price()
        db.session.commit()

        return make_response(jsonify({'message': 'Order updated successfully', 'total_price': order.total_price}), 200)
    
    def delete(self, order_id):
        order = Orders.query.get_or_404(order_id)
        db.session.delete(order)
        db.session.commit()

        return make_response(jsonify({'message': f'Order {order_id} deleted successfully'}), 204)


# Register the UploadImage resource with the API
api.add_resource(UploadImage, '/upload')
api.add_resource(OrdersResource, '/orders', '/orders/<int:order_id>')

if __name__ == '__main__':
    app.run(debug=True)