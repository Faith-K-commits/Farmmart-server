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

# Resource for CRUD operations on Animal entities
class AnimalResource(Resource):
    
    # GET method to retrieve animals
    def get(self, animal_id=None):
        if animal_id:
            # Fetch a single animal by ID
            animal = db.session.get(Animal, animal_id)
            if not animal:
                return make_response(jsonify({"error": "No animal found with this ID!"}), 404)
            return make_response(jsonify(animal.to_dict()), 200)
        
        # Pagination: retrieve 'page' and 'per_page' from query parameters, with defaults
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        try:
            # Query and paginate animals, based on requested page and per_page
            animals_query = Animal.query.paginate(page=page, per_page=per_page, error_out=False)
            
            # Serialize the animals on the current page
            animals = [animal.to_dict() for animal in animals_query.items]
            
            # Add pagination metadata
            pagination_info = {
                "total_items": animals_query.total,
                "total_pages": animals_query.pages,
                "current_page": animals_query.page,
                "per_page": animals_query.per_page,
                "has_next": animals_query.has_next,
                "has_prev": animals_query.has_prev,
            }

            # Return animals and pagination info
            return make_response(jsonify({"animals": animals, "pagination": pagination_info}), 200)

        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)

    # POST method to create a new animal entry
    def post(self):
        data = request.form.to_dict()  # Get other form data as a dictionary
        try:
            if 'file' in request.files:
                file = request.files['file']
                if file.filename != '':
                    # Upload the file to Cloudinary
                    result = cloudinary.uploader.upload(file)
                    data['image_url'] = result['secure_url']
            
            # Create and save new Animal instance
            animal = Animal(**data)
            db.session.add(animal)
            db.session.commit()
            return make_response(jsonify(animal.to_dict()), 201)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"error": str(e)}), 400)

    # PATCH method to update an existing animal entry
    def patch(self, animal_id):
        animal = db.session.get(Animal, animal_id)
        if not animal:
            return make_response(jsonify({"error": "No animal found with this ID!"}), 404)
        
        data = request.form.to_dict()
        try:
            for key, value in data.items():
                setattr(animal, key, value)

            # Handle image update
            if 'file' in request.files:
                file = request.files['file']
                if file.filename != '':
                    result = cloudinary.uploader.upload(file)
                    animal.image_url = result['secure_url']

            db.session.commit()
            return make_response(jsonify(animal.to_dict()), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"error": str(e)}), 400)

    # DELETE method to remove an animal entry by ID
    def delete(self, animal_id):
        animal = db.session.get(Animal, animal_id)
        if not animal:
            return make_response(jsonify({"error": "Animal with this ID not found!"}), 404)
        try:
            db.session.delete(animal)
            db.session.commit()
            return make_response(jsonify({"message": "Animal deleted successfully"}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"error": str(e)}), 400)
    
class AnimalSearchResource(Resource):
    # Search endpoint: /animals/search
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category', type=str)
        breed = request.args.get('breed', type=str)

        # Start with base query
        query = Animal.query

        # Apply search filters
        if category:
            query = query.filter(Animal.category.ilike(f"%{category}%"))
        if breed:
            query = query.filter(Animal.breed.ilike(f"%{breed}%"))

        # Paginate the search results
        animals_query = query.paginate(page=page, per_page=per_page, error_out=False)
        animals = [animal.to_dict() for animal in animals_query.items]

        # Pagination metadata
        pagination_info = {
            "total_items": animals_query.total,
            "total_pages": animals_query.pages,
            "current_page": animals_query.page,
            "per_page": animals_query.per_page,
            "has_next": animals_query.has_next,
            "has_prev": animals_query.has_prev,
        }

        return make_response(jsonify({"animals": animals, "pagination": pagination_info}), 200)

class AnimalFilterResource(Resource):
    # Filter endpoint: /animals/filter
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        breed = request.args.get('breed', type=str)
        age_min = request.args.get('age_min', type=int)
        age_max = request.args.get('age_max', type=int)

        # Start with base query
        query = Animal.query

        # Apply filter criteria
        if breed:
            query = query.filter(Animal.breed.ilike(f"%{breed}%"))
        if age_min is not None:
            query = query.filter(Animal.age >= age_min)
        if age_max is not None:
            query = query.filter(Animal.age <= age_max)

        # Paginate the filtered results
        animals_query = query.paginate(page=page, per_page=per_page, error_out=False)
        animals = [animal.to_dict() for animal in animals_query.items]

        # Pagination metadata
        pagination_info = {
            "total_items": animals_query.total,
            "total_pages": animals_query.pages,
            "current_page": animals_query.page,
            "per_page": animals_query.per_page,
            "has_next": animals_query.has_next,
            "has_prev": animals_query.has_prev,
        }

        return make_response(jsonify({"animals": animals, "pagination": pagination_info}), 200)
    
# Register the resource with the API
api.add_resource(UploadImage, '/upload')
api.add_resource(AnimalResource, '/animals', '/animals/<int:animal_id>')
api.add_resource(AnimalSearchResource, '/animals/search')
api.add_resource(AnimalFilterResource, '/animals/filter')
api.add_resource(OrdersResource, '/orders', '/orders/<int:order_id>')
api.add_resource(OrderItemResource, '/orderitems', '/orderitems/<int:order_item_id>')
api.add_resource(PaymentResource, '/payments', '/payments/<int:payment_id>')

if __name__ == '__main__':
    app.run(debug=True)