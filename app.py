from flask import make_response, jsonify, request
from flask_restful import Resource
from config import db, app, api
from models import Animal, Orders, OrderItem, Payments
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
            # Fetch a single order by its ID
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
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 5, type=int)
            paginated_orders = Orders.query.paginate(page=page, per_page=per_page, error_out=False)
            orders = paginated_orders.items
            orders_data = [{
                'id': order.id,
                'user_id': order.user_id,
                'status': order.status,
                'total_price': order.calculate_total_price(),
                'created_at': order.created_at,
                'updated_at': order.updated_at
            } for order in orders]
            
            response = {
                'orders': orders_data,
                'meta': {
                    'current_page': paginated_orders.page,
                    'per_page': paginated_orders.per_page,
                    'total_items': paginated_orders.total,
                    'total_pages': paginated_orders.pages,
                    'has_next': paginated_orders.has_next,
                    'has_prev': paginated_orders.has_prev,
                    'next_page': paginated_orders.next_num if paginated_orders.has_next else None,
                    'prev_page': paginated_orders.prev_num if paginated_orders.has_prev else None
                }
            }
            
            return make_response(jsonify(response), 200)

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

class OrderItemResource(Resource):
    def get(self, order_item_id=None):
        if order_item_id:
            item = OrderItem.query.get_or_404(order_item_id)
            item_data = {
                'id': item.id,
                'order_id': item.order_id,
                'animal_id': item.animal_id,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'subtotal': item.subtotal
            }
            return make_response(jsonify(item_data), 200)
        else:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 5, type=int)
            paginated_order_items = OrderItem.query.paginate(page=page, per_page=per_page, error_out=False)
            items = paginated_order_items.items
            items_data = [
                {
                'id': item.id,
                'order_id': item.order_id,
                'animal_id': item.animal_id,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'subtotal': item.subtotal
            } for item in items
            ]
            response = {
                'items': items_data,
                'meta': {
                    'current_page': paginated_order_items.page,
                    'per_page': paginated_order_items.per_page,
                    'total_items': paginated_order_items.total,
                    'total_pages': paginated_order_items.pages,
                    'has_next': paginated_order_items.has_next,
                    'has_prev': paginated_order_items.has_prev,
                    'next_page': paginated_order_items.next_num if paginated_order_items.has_next else None,
                    'prev_page': paginated_order_items.prev_num if paginated_order_items.has_prev else None
                }
            }
            
            return make_response(jsonify(response), 200)

    def post(self):
        data = request.get_json()

        # Validate price and quantity
        if data.get('quantity') <= 0 or data.get('unit_price') <= 0:
            return {'error': 'Invalid quantity or unit price'}, 400

        order_item = OrderItem(
            order_id=data['order_id'],
            animal_id=data['animal_id'],
            quantity=data['quantity'],
            unit_price=data['unit_price'],
            subtotal=data['quantity'] * data['unit_price']
        )

        db.session.add(order_item)
        db.session.commit()

        # Recalculate total price for the related order
        order = Orders.query.get(data['order_id'])
        order.total_price = order.calculate_total_price()
        db.session.commit()

        return make_response(jsonify({'message': 'Order Item added successfully', 'id': order_item.id}), 201)

class PaymentResource(Resource):
    
    def get(self, payment_id=None):
        if payment_id:
            payment = Payments.query.get_or_404(payment_id)
            payment_data = {
                'id': payment.id,
                'order_id': payment.order_id,
                'user_id': payment.user_id,
                'amount': payment.amount,
                'status': payment.status,
                'payment_date': payment.payment_date
            }
            return make_response(jsonify(payment_data), 200)
        else:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 5, type=int)
            paginated_payments = Payments.query.paginate(page=page, per_page=per_page, error_out=False)
            payments = paginated_payments.items

            payments_data = [{
                'id': payment.id,
                'order_id': payment.order_id,
                'user_id': payment.user_id,
                'amount': payment.amount,
                'status': payment.status,
                'payment_date': payment.payment_date
            } for payment in payments]

            response = {
                'payments': payments_data,
                'meta': {
                    'current_page': paginated_payments.page,
                    'per_page': paginated_payments.per_page,
                    'total_items': paginated_payments.total,
                    'total_pages': paginated_payments.pages,
                    'has_next': paginated_payments.has_next,
                    'has_prev': paginated_payments.has_prev,
                    'next_page': paginated_payments.next_num if paginated_payments.has_next else None,
                    'prev_page': paginated_payments.prev_num if paginated_payments.has_prev else None
                }
            }
            return make_response(jsonify(response), 200)

    def post(self):
        data = request.get_json()

        # Validate payment status
        if data.get('status') not in ['Pending', 'Paid', 'Failed']:
            return {'error': 'Invalid payment status'}, 400

        # Create new payment entry
        payment = Payments(
            order_id=data['order_id'],
            user_id=data['user_id'],
            amount=data['amount'],
            status=data['status']
        )

        db.session.add(payment)
        db.session.commit()

        return make_response(jsonify({'message': 'Payment created successfully', 'id': payment.id}), 201)

# Register the UploadImage resource with the API
api.add_resource(UploadImage, '/upload')
api.add_resource(OrdersResource, '/orders', '/orders/<int:order_id>')
api.add_resource(OrderItemResource, '/orderitems', '/orderitems/<int:order_item_id>')
api.add_resource(PaymentResource, '/payments', '/payments/<int:payment_id>')

if __name__ == '__main__':
    app.run(debug=True)