from functools import wraps
from flask import make_response, jsonify, request, current_app
from flask_restful import Resource
from config import db, app, api
from models import Animal, Orders, OrderItem, Payments, Cart, CartItem, BaseUser, Vendor, User
import cloudinary.uploader
from datetime import datetime, timedelta 
from flask_login import login_user, logout_user, login_required
import jwt
import random
import json


@app.route('/')
def home():
    return 'Welcome to the Home Page'

@app.route('/ci')
def ci():
    return 'Welcome to the CI/CD with Github Actions'

# # Resource for uploading images to Cloudinary (Testing if cloudinary is available and functioning properly)
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
            order = Orders.query.filter_by(id=order_id).first()
            if not order:
                return make_response(jsonify({'error': 'Order not found!'}), 404)
            order_data = order.to_dict()

            return make_response(jsonify(order_data), 200)
        else:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 5, type=int)
            paginated_orders = Orders.query.paginate(page=page, per_page=per_page, error_out=False)
            orders = paginated_orders.items

            orders_data = [order.to_dict() for order in orders]

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
        order = Orders(user_id=request.user_id, status=data['status'])
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
    def get(self, animal_id=None):
        if animal_id:
            animal = db.session.get(Animal, animal_id)
            if not animal:
                return make_response(jsonify({"error": "No animal found with this ID!"}), 404)

            vendor = db.session.get(BaseUser, animal.user_id)
            animal_data = animal.to_dict()
            if vendor and vendor.role == "vendor":
                animal_data.update({
                    "vendor_name": vendor.name,
                    "farm_name": vendor.farm_name,
                    "phone_number": vendor.phone_number,
                    "email": vendor.email
                })
            return make_response(jsonify(animal_data), 200)

        # Paginate all animals
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        animals_query = Animal.query.paginate(page=page, per_page=per_page, error_out=False)
        animals = [animal.to_dict() for animal in animals_query.items]

        pagination_info = {
            "total_items": animals_query.total,
            "total_pages": animals_query.pages,
            "current_page": animals_query.page,
            "per_page": animals_query.per_page,
            "has_next": animals_query.has_next,
            "has_prev": animals_query.has_prev,
        }
        return make_response(jsonify({"animals": animals, "pagination": pagination_info}), 200)

    def post(self):
        data = request.form.to_dict()
        try:
            if 'file' in request.files:
                file = request.files['file']
                if file.filename:
                    result = cloudinary.uploader.upload(file)
                    data['image_url'] = result['secure_url']

            animal = Animal(**data)
            db.session.add(animal)
            db.session.commit()
            return make_response(jsonify(animal.to_dict()), 201)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"error": str(e)}), 400)

    def patch(self, animal_id):
        animal = db.session.get(Animal, animal_id)
        if not animal:
            return make_response(jsonify({"error": "No animal found with this ID!"}), 404)

        data = request.form.to_dict()
        try:
            for key, value in data.items():
                setattr(animal, key, value)
            if 'file' in request.files:
                file = request.files['file']
                if file.filename:
                    result = cloudinary.uploader.upload(file)
                    animal.image_url = result['secure_url']
            db.session.commit()
            return make_response(jsonify(animal.to_dict()), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"error": str(e)}), 400)

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
    def get(self):
        category = request.args.get('category', type=str)
        breed = request.args.get('breed', type=str)

        query = Animal.query
        if category:
            query = query.filter(Animal.category.ilike(f"%{category}%"))
        if breed:
            query = query.filter(Animal.breed.ilike(f"%{breed}%"))

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        animals_query = query.paginate(page=page, per_page=per_page, error_out=False)
        animals = [animal.to_dict() for animal in animals_query.items]

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
    def get(self):
        breed = request.args.get('breed', type=str)
        age_min = request.args.get('age_min', type=int)
        age_max = request.args.get('age_max', type=int)

        query = Animal.query
        if breed:
            query = query.filter(Animal.breed.ilike(f"%{breed}%"))
        if age_min is not None:
            query = query.filter(Animal.age >= age_min)
        if age_max is not None:
            query = query.filter(Animal.age <= age_max)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        animals_query = query.paginate(page=page, per_page=per_page, error_out=False)
        animals = [animal.to_dict() for animal in animals_query.items]

        pagination_info = {
            "total_items": animals_query.total,
            "total_pages": animals_query.pages,
            "current_page": animals_query.page,
            "per_page": animals_query.per_page,
            "has_next": animals_query.has_next,
            "has_prev": animals_query.has_prev,
        }
        return make_response(jsonify({"animals": animals, "pagination": pagination_info}), 200)

# Resource to get unique animal categories
class CategoryResource(Resource):
    def get(self):
        # Query distinct categories from the Animal model
        categories = Animal.query.with_entities(Animal.category).distinct().all()
        # Convert categories to a list of strings and return as JSON
        return jsonify([category[0] for category in categories])

# Resource to get unique animal breeds
class BreedResource(Resource):
    def get(self):
        # Query distinct breeds from the Animal model
        breeds = Animal.query.with_entities(Animal.breed).distinct().all()
        # Convert breeds to a list of strings and return as JSON
        return jsonify([breed[0] for breed in breeds])

# Fetches Random selection of animals
@app.route("/animals/featured", methods=["GET"])
def get_featured_animals():
    try:
        # Fetch a random selection of 5 animals
        random_animals = Animal.query.order_by(db.func.random()).limit(5).all()
        animals_data = [animal.to_dict() for animal in random_animals]
        return jsonify({"featured_animals": animals_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

## Cart Resource - Retrieve the user's cart
# class CartResource(Resource):
#     def serialize_datetime(self, obj):
#         """
#         Serializes datetime objects into string format.
#         """
#         if isinstance(obj, datetime):
#             return obj.isoformat()  # Convert datetime to ISO 8601 string format
#         raise TypeError("Type not serializable")

#     def get(self, user_id):
#         """
#         Retrieve the user's cart details by user ID.
#         If the cart doesn't exist, return a 404 error.
#         """
#         # Find or create a cart associated with the given user_id
#         cart = Cart.query.filter_by(user_id=user_id).first()
#         if not cart:
#             cart = Cart(user_id=user_id)
#             db.session.add(cart)
#             db.session.commit()

#         # Get cart items with animal names
#         cart_items = []
#         for cart_item in cart.cart_items:
#             animal = db.session.get(Animal, cart_item.animal_id)
#             if animal:
#                 cart_items.append({
#                     "id": cart_item.id,
#                     "cart_id": cart_item.cart_id,
#                     "animal_id": cart_item.animal_id,
#                     "quantity": cart_item.quantity,
#                     "added_at": self.serialize_datetime(cart_item.added_at),  # Serialize datetime
#                     "animal_name": animal.name  # Add the animal name to the cart item
#                 })

#         # Return the cart details along with animal names
#         response = {
#             "status": "success",
#             "cart": {
#                 "id": cart.id,
#                 "user_id": cart.user_id,
#                 "created_at": self.serialize_datetime(cart.created_at),  # Serialize datetime
#                 "cart_items": cart_items
#             }
#         }

#         # Use jsonify to automatically convert the response to JSON
#         return jsonify(response)

# class AddItemToCartResource(Resource):
#     def post(self, user_id):
#         """
#         Add an item to the user's cart.
#         """
#         data = request.get_json()
#         animal_id = data.get('animal_id')
#         quantity = data.get('quantity')

#         if not animal_id or not quantity or quantity <= 0:
#             return {"status": "error", "message": "Invalid animal_id or quantity"}, 400

#         # Retrieve the user's cart, create one if it doesn't exist
#         cart = Cart.query.filter_by(user_id=user_id).first()
#         if not cart:
#             cart = Cart(user_id=user_id)
#             db.session.add(cart)

#         # Check if the animal exists in the database
#         animal = Animal.query.get(animal_id)
#         if not animal:
#             return {"status": "error", "message": "Animal not found"}, 404

#         # Check if the requested quantity exceeds available available_quantity
#         if animal.available_quantity < quantity:
#             return {"status": "error", "message": "Not enough available_quantity available"}, 400

#         # Check if the animal is already in the cart
#         cart_item = CartItem.query.filter_by(cart_id=cart.id, animal_id=animal_id).first()
#         if cart_item:
#             # If the item is already in the cart, just update the quantity
#             cart_item.quantity += quantity
#         else:
#             # If the item isn't in the cart, create a new cart item
#             cart_item = CartItem(cart_id=cart.id, animal_id=animal_id, quantity=quantity)
#             db.session.add(cart_item)

#         # Adjust the animal available_quantity accordingly
#         animal.available_quantity -= quantity

#         try:
#             db.session.commit()  # Commit changes
#         except Exception as e:
#             db.session.rollback()
#             return {"status": "error", "message": "Failed to add item to cart"}, 500

#         return {
#             "status": "success",
#             "message": "Item added to cart",
#             "cart_item": cart_item.to_dict()
#         }, 201

# class UpdateCartItemQuantityResource(Resource):
#     def put(self, user_id, animal_id):
#         """
#         Update the quantity of an item in the user's cart and adjust available_quantity.
#         """
#         data = request.get_json()
#         new_quantity = data.get('quantity')

#         if not new_quantity or new_quantity <= 0:
#             return {"status": "error", "message": "Quantity must be greater than 0"}, 400

#         # Retrieve the user's cart
#         cart = Cart.query.filter_by(user_id=user_id).first()
#         if not cart:
#             return {"status": "error", "message": "Cart not found"}, 404

#         # Find the cart item to update
#         cart_item = CartItem.query.filter_by(cart_id=cart.id, animal_id=animal_id).first()
#         if not cart_item:
#             return {"status": "error", "message": "Item not in cart"}, 404

#         # Check available_quantity availability for the new quantity
#         animal = Animal.query.get(animal_id)
#         if animal and animal.available_quantity < new_quantity - cart_item.quantity:
#             return {"status": "error", "message": "Not enough available_quantity"}, 400

#         # Update item quantity and adjust animal available_quantity
#         if animal:
#             stock_diff = new_quantity - cart_item.quantity
#             if stock_diff > 0:
#                 animal.available_quantity -= stock_diff  # Subtract from available_quantity when quantity increases
#             elif stock_diff < 0:
#                 animal.available_quantity += abs(stock_diff)  # Add to available_quantity when quantity decreases

#         cart_item.quantity = new_quantity
#         try:
#             db.session.commit()  # Commit changes
#         except Exception as e:
#             db.session.rollback()
#             return {"status": "error", "message": "Failed to update item quantity"}, 500

#         return {"status": "success", "message": "Item quantity updated", "cart_item": cart_item.to_dict()}, 200

# class RemoveItemFromCartResource(Resource):
#     def delete(self, user_id, animal_id):
#         """
#         Remove an item from the user's cart and restore available_quantity.
#         """
#         # Retrieve the user's cart
#         cart = Cart.query.filter_by(user_id=user_id).first()
#         if not cart:
#             return {"status": "error", "message": "Cart not found"}, 404

#         # Find the cart item to remove
#         cart_item = CartItem.query.filter_by(cart_id=cart.id, animal_id=animal_id).first()
#         if not cart_item:
#             return {"status": "error", "message": "Item not in cart"}, 404

#         # Restore the available_quantity and delete the item from the cart
#         animal = Animal.query.get(animal_id)
#         if animal:
#             animal.available_quantity += cart_item.quantity  # Add quantity back to available_quantity

#         try:
#             db.session.delete(cart_item)  # Remove item from cart
#             db.session.commit()  # Commit the transaction
#         except Exception as e:
#             db.session.rollback()
#             return {"status": "error", "message": "Failed to remove item"}, 500

#         return {"status": "success", "message": "Item removed from cart"}, 204

# class CheckoutCartResource(Resource):
#     def post(self, user_id):
#         """
#         Finalize the cart by converting it into an order and clearing the cart.
#         """
#         # Retrieve the user's cart
#         cart = Cart.query.filter_by(user_id=user_id).first()
#         if not cart or not cart.cart_items:
#             return {"status": "error", "message": "Cart is empty"}, 400

#         # Calculate the total price of all cart items
#         total_price = sum(item.animal.price * item.quantity for item in cart.cart_items)

#         # Validate total price
#         if total_price <= 0:
#             return {"status": "error", "message": "Total price cannot be zero or negative"}, 400

#         # Create a new order with the calculated total price
#         order = Orders(user_id=user_id, total_price=total_price, created_at=datetime.utcnow())
#         db.session.add(order)

#         # Transfer each item to the order and clear the cart
#         for cart_item in cart.cart_items:
#             cart_item.order = order  # Associate item with order
#             db.session.delete(cart_item)  # Remove item from cart

#         try:
#             db.session.commit()  # Commit the transaction
#         except Exception as e:
#             db.session.rollback()
#             return {"status": "error", "message": "Checkout failed"}, 500

#         return {"status": "success", "message": "Checkout complete", "order": order.to_dict()}, 200
# class CartItemsResource(Resource):
#     def get(self, user_id):
#         """
#         Retrieve paginated items from the user's cart.
#         Supports 'page' and 'per_page' query parameters.
#         """
#         # Retrieve the user's cart
#         cart = Cart.query.filter_by(user_id=user_id).first()
#         if not cart:
#             return {"status": "error", "message": "Cart not found"}, 404

#         # Get pagination parameters from the request
#         page = request.args.get('page', 1, type=int)
#         per_page = request.args.get('per_page', 10, type=int)
#         per_page = min(per_page, 100)  # Limit to a maximum of 100 items per page

#         # Paginate the cart items query
#         cart_items_query = CartItem.query.filter_by(cart_id=cart.id)
#         cart_items = cart_items_query.paginate(page, per_page, False)

#         # Serialize paginated items
#         items_data = [item.to_dict() for item in cart_items.items]
#         return {
#             "status": "success",
#             "cart_items": items_data,
#             "total_items": cart_items.total,
#             "total_pages": cart_items.pages,
#             "current_page": cart_items.page
#         }, 200
    
class CartResource(Resource): 
    def serialize_datetime(self, obj):
        """
        Serializes datetime objects into string format.
        """
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to ISO 8601 string format
        raise TypeError("Type not serializable")

    def get(self, user_id):
        """
        Retrieve the user's cart details by user ID.
        If the cart doesn't exist, return a 404 error.
        """
        cart = Cart.query.filter_by(user_id=user_id).first()

        if not cart:
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.commit()

        # Get cart items with animal details
        cart_items = []
        for cart_item in cart.cart_items:
            animal = db.session.get(Animal, cart_item.animal_id)
            if animal:
                cart_items.append({
                    "id": cart_item.id,
                    "cart_id": cart_item.cart_id,
                    "animal_id": cart_item.animal_id,
                    "quantity": cart_item.quantity,
                    "added_at": self.serialize_datetime(cart_item.added_at),
                    "animal_name": animal.name,
                    "animal_price": animal.price,  # Adding animal price to the cart item
                    "animal_image_url": animal.image_url,  # Adding animal image URL to the cart item
                })

        # Ensure that the total price calculation is correct, even when there are no cart items
        total_price = sum(item['animal_price'] * item['quantity'] for item in cart_items)

        response = {
            "status": "success",
            "cart": {
                "id": cart.id,
                "user_id": cart.user_id,
                "created_at": self.serialize_datetime(cart.created_at),
                "updated_at": self.serialize_datetime(cart.updated_at) if cart.updated_at else None,
                "total_price": total_price,  # Correctly calculate total price
                "cart_items": cart_items  # Empty array if no items in cart
            }
        }

        # Debugging: Log the response object to verify its structure (remove in production)
        print(f"Response data for user {user_id}: {response}")
        
        return jsonify(response)
    
class AddItemToCartResource(Resource):
    def post(self, user_id):
        """
        Add an item to the user's cart.
        """
        data = request.get_json()
        animal_id = data.get('animal_id')
        quantity = data.get('quantity')

        if not animal_id or not quantity or quantity <= 0:
            return {"status": "error", "message": "Invalid animal_id or quantity"}, 400

        # Retrieve the user's cart, create one if it doesn't exist
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.session.add(cart)

        # Check if the animal exists in the database
        animal = Animal.query.get(animal_id)
        if not animal:
            return {"status": "error", "message": "Animal not found"}, 404

        # Check if the requested quantity exceeds available_quantity
        if animal.available_quantity < quantity:
            return {"status": "error", "message": "Not enough available quantity available"}, 400

        # Check if the animal is already in the cart
        cart_item = CartItem.query.filter_by(cart_id=cart.id, animal_id=animal_id).first()
        if cart_item:
            # If the item is already in the cart, just update the quantity
            cart_item.quantity += quantity
        else:
            # If the item isn't in the cart, create a new cart item
            cart_item = CartItem(cart_id=cart.id, animal_id=animal_id, quantity=quantity)
            db.session.add(cart_item)

        # Adjust the animal available_quantity accordingly
        animal.available_quantity -= quantity

        try:
            db.session.commit()  # Commit changes
        except Exception as e:
            db.session.rollback()
            return {"status": "error", "message": "Failed to add item to cart"}, 500

        return {
            "status": "success",
            "message": "Item added to cart",
            "cart_item": cart_item.to_dict(include_animal=True)
        }, 201

class UpdateCartItemQuantityResource(Resource):
    def put(self, user_id, animal_id):
        """
        Update the quantity of an item in the user's cart and adjust available_quantity.
        """
        data = request.get_json()
        new_quantity = data.get('quantity')

        if not new_quantity or new_quantity <= 0:
            return {"status": "error", "message": "Quantity must be greater than 0"}, 400

        # Retrieve the user's cart
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            return {"status": "error", "message": "Cart not found"}, 404

        # Find the cart item to update
        cart_item = CartItem.query.filter_by(cart_id=cart.id, animal_id=animal_id).first()
        if not cart_item:
            return {"status": "error", "message": "Item not in cart"}, 404

        # Check available_quantity availability for the new quantity
        animal = Animal.query.get(animal_id)
        if animal and animal.available_quantity < new_quantity - cart_item.quantity:
            return {"status": "error", "message": "Not enough available quantity"}, 400

        # Update item quantity and adjust animal available_quantity
        if animal:
            stock_diff = new_quantity - cart_item.quantity
            if stock_diff > 0:
                animal.available_quantity -= stock_diff
            elif stock_diff < 0:
                animal.available_quantity += abs(stock_diff)

        cart_item.quantity = new_quantity
        try:
            db.session.commit()  # Commit changes
        except Exception as e:
            db.session.rollback()
            return {"status": "error", "message": "Failed to update item quantity"}, 500

        return {
            "status": "success",
            "message": "Item quantity updated",
            "cart_item": cart_item.to_dict(include_animal=True)
        }, 200

class RemoveItemFromCartResource(Resource):
    def delete(self, user_id, animal_id):
        """
        Remove an item from the user's cart and restore the available_quantity.
        """
        # Retrieve the user's cart
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            return {"status": "error", "message": "Cart not found"}, 404

        # Find the cart item to remove
        cart_item = CartItem.query.filter_by(cart_id=cart.id, animal_id=animal_id).first()
        if not cart_item:
            return {"status": "error", "message": "Item not in cart"}, 404

        # Restore the available_quantity of the animal
        animal = Animal.query.get(animal_id)
        if animal:
            animal.available_quantity += cart_item.quantity
        else:
            return {"status": "error", "message": "Animal not found"}, 404

        try:
            db.session.delete(cart_item)  # Delete the cart item
            db.session.commit()  # Commit the changes
        except Exception as e:
            db.session.rollback()
            return {"status": "error", "message": "Failed to remove item from cart"}, 500

        return {"status": "success", "message": "Item removed from cart"}, 204

class CheckoutCartResource(Resource):
    def post(self, user_id):
        """
        Finalize the cart by converting it into an order and clearing the cart.
        """
        # Retrieve the user's cart
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart or not cart.cart_items:
            return {"status": "error", "message": "Cart is empty"}, 400

        # Calculate the total price of all cart items
        total_price = sum(item.animal.price * item.quantity for item in cart.cart_items)

        # Validate total price
        if total_price <= 0:
            return {"status": "error", "message": "Total price cannot be zero or negative"}, 400

        # Create a new order with the calculated total price
        order = Orders(user_id=user_id, total_price=total_price, created_at=datetime.utcnow())
        db.session.add(order)

        # Transfer each item to the order and clear the cart
        for cart_item in cart.cart_items:
            cart_item.order = order  # Associate each cart item with the new order
            db.session.delete(cart_item)  # Remove items from the cart

        try:
            db.session.commit()  # Commit the order and cart changes
        except Exception as e:
            db.session.rollback()
            return {"status": "error", "message": "Checkout failed"}, 500

        return {
            "status": "success",
            "message": "Checkout successful",
            "order_id": order.id,
            "total_price": total_price
        }, 201

@app.route('/cart/<int:cart_id>', methods=['GET'])
def get_cart(cart_id):
    """
    Get cart by ID (useful if you need to access a specific cart, 
    e.g., for admin or debugging purposes).
    """
    cart = Cart.query.get_or_404(cart_id)
    return jsonify(cart.to_dict())
    
#Vendor Animal management Resources
#Allows vendors to add new animals
class VendorAnimalsResource(Resource):
    def post(self):
        """Add a new animal for the authenticated vendor."""
        auth_header = request.headers.get("Authorization")
        if not auth_header or " " not in auth_header:
            return {"error": "Authorization header missing or malformed"}, 401

        token = auth_header.split(" ")[1]
        try:
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired"}, 401
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}, 401

        vendor = db.session.get(BaseUser, decoded_token.get("id"))
        if not vendor or vendor.role != "vendor":
            return {"error": "Unauthorized access"}, 401

        # Parse animal data
        data = request.form.to_dict()
        data['user_id'] = vendor.id  # Ensure this matches the model definition

        # Handle image upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename:
                result = cloudinary.uploader.upload(file)
                data['image_url'] = result['secure_url']

        # Validate and create animal
        try:
            # Use only valid fields from the Animal model
            valid_keys = [column.key for column in Animal.__table__.columns]
            filtered_data = {key: value for key, value in data.items() if key in valid_keys}

            animal = Animal(**filtered_data)
            db.session.add(animal)
            db.session.commit()
            return make_response(jsonify(animal.to_dict()), 201)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"error": str(e)}), 400)
        
# Fetches all animals belonging to a specific vendor.
class VendorAnimalListResource(Resource):
    def get(self):
        """Fetch all animals associated with the authenticated vendor."""
        auth_header = request.headers.get("Authorization")
        if not auth_header or " " not in auth_header:
            return {"error": "Authorization header missing or malformed"}, 401

        token = auth_header.split(" ")[1]
        try:
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired"}, 401
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}, 401

        vendor = BaseUser.query.get(decoded_token.get("id"))
        if not vendor or vendor.role != "vendor":
            return {"error": "Unauthorized access"}, 401

        animals = Animal.query.filter_by(user_id=vendor.id).all()
        animals_data = [animal.to_dict() for animal in animals]
        return jsonify({"animals": animals_data})

#Allows vendors to update animals they own
class VendorAnimalUpdateResource(Resource):
    def patch(self, animal_id):
        """Update details of an animal owned by the authenticated vendor."""
        auth_header = request.headers.get("Authorization")
        if not auth_header or " " not in auth_header:
            return {"error": "Authorization header missing or malformed"}, 401

        token = auth_header.split(" ")[1]
        try:
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired"}, 401
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}, 401

        vendor = BaseUser.query.get(decoded_token.get("id"))
        if not vendor or vendor.role != "vendor":
            return {"error": "Unauthorized access"}, 401

        animal = Animal.query.get(animal_id)
        if not animal or animal.user_id != vendor.id:
            return {"error": "Animal not found or unauthorized"}, 404

        data = request.form.to_dict()
        if 'file' in request.files:
            file = request.files['file']
            if file.filename:
                result = cloudinary.uploader.upload(file)
                data['image_url'] = result['secure_url']

        try:
            for key, value in data.items():
                setattr(animal, key, value)
            db.session.commit()
            return jsonify(animal.to_dict())
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

#Allows vendors to delete animals they own
class VendorAnimalDeleteResource(Resource):
    def delete(self, animal_id):
        """Delete an animal owned by the authenticated vendor."""
        auth_header = request.headers.get("Authorization")
        if not auth_header or " " not in auth_header:
            return {"error": "Authorization header missing or malformed"}, 401

        token = auth_header.split(" ")[1]
        try:
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired"}, 401
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}, 401

        vendor = BaseUser.query.get(decoded_token.get("id"))
        if not vendor or vendor.role != "vendor":
            return {"error": "Unauthorized access"}, 401

        animal = Animal.query.get(animal_id)
        if not animal or animal.user_id != vendor.id:
            return {"error": "Animal not found or unauthorized"}, 404

        try:
            db.session.delete(animal)
            db.session.commit()
            return {"message": "Animal deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400
        
# Register the resource with the API
api.add_resource(UploadImage, '/upload')
api.add_resource(AnimalResource, '/animals', '/animals/<int:animal_id>')
api.add_resource(AnimalSearchResource, '/animals/search')
api.add_resource(AnimalFilterResource, '/animals/filter')
api.add_resource(OrdersResource, '/orders', '/orders/<int:order_id>')
api.add_resource(OrderItemResource, '/orderitems', '/orderitems/<int:order_item_id>')
api.add_resource(PaymentResource, '/payments', '/payments/<int:payment_id>')
api.add_resource(CartResource, '/cart/<int:user_id>')
api.add_resource(AddItemToCartResource, '/cart/<int:user_id>/add')
api.add_resource(UpdateCartItemQuantityResource, '/cart/<int:user_id>/update/<int:animal_id>')
api.add_resource(RemoveItemFromCartResource, '/cart/<int:user_id>/remove/<int:animal_id>')
api.add_resource(CheckoutCartResource, '/cart/<int:user_id>/checkout')
api.add_resource(CategoryResource, '/categories')
api.add_resource(BreedResource, '/breeds')
api.add_resource(VendorAnimalsResource, '/vendor/animals')
api.add_resource(VendorAnimalListResource, '/vendor/animals/list')
api.add_resource(VendorAnimalUpdateResource, '/vendor/animals/<int:animal_id>')
api.add_resource(VendorAnimalDeleteResource, '/vendor/animals/delete/<int:animal_id>')




### USER-SPECIFIC RESOURCES ###
class RegisterResource(Resource):
    def post(self):
        data = request.get_json()

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'customer')  # Default to 'customer' if not provided

        # Additional fields for vendors
        phone_number = data.get('phone_number')
        farm_name = data.get('farm_name')

        # Validate required fields
        if not all([name, email, password]):
            return {'error': 'Name, email, and password are required'}, 400

        # Validate email format
        if not BaseUser.is_valid_email(email):
            return {'error': 'Enter a valid email'}, 400

        # Check if the email is already in use
        existing_user = BaseUser.query.filter_by(email=email).first()
        if existing_user:
            return {'error': 'Email already in use'}, 400

        # Create the appropriate user role
        try:
            if role == 'vendor':
                if not phone_number or not farm_name:
                    return {'error': 'Phone number and farm name are required for vendors'}, 400
                new_user = Vendor(
                    name=name,
                    email=email,
                    role=role,
                    phone_number=phone_number,
                    farm_name=farm_name
                )
            else:  # Default to creating a regular customer
                new_user = User(
                    name=name,
                    email=email,
                    role=role
                )
            
            # Hash and set the password
            new_user.set_password(password)

            # Save to the database
            db.session.add(new_user)
            db.session.commit()
            return {'message': 'User created successfully', 'user': new_user.serialize()}, 201

        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500


api.add_resource(RegisterResource, '/register')


class UserListResource(Resource):
    def get(self):
        
        try:
            # Retrieve pagination parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)

            # Validation for positive page and per_page values
            if page <= 0 or per_page <= 0:
                return {'error': 'Page and per_page must be greater than 0'}, 400

            # Query all base_users (admin, customer, vendor) and paginate
            paginated_users = BaseUser.query.paginate(page=page, per_page=per_page, error_out=False)

            # Serialize users (this includes all types: admin, customer, vendor)
            users = [user.serialize() for user in paginated_users.items]

            # Return pagination info along with user data
            return {
                'users': users,
                'total': paginated_users.total,
                'pages': paginated_users.pages,
                'current_page': paginated_users.page,
                'per_page': paginated_users.per_page
            }, 200

        except Exception as e:
            return {'error': str(e)}, 500

api.add_resource(UserListResource, '/users')  # Ensure endpoint uses plural 'users'


class DeleteUserResource(Resource):
    def delete(self, user_id):
        """Deletes a user by their ID."""
        try:
            # Fetch the user from the database
            user = BaseUser.query.get(user_id)
            
            if not user:
                return {'error': f'User with ID {user_id} not found'}, 404

            # Perform any user-specific cleanup if required (e.g., related data)
            if isinstance(user, Vendor):
                # Cleanup specific to vendors (e.g., delete animals or associated resources)
                for animal in user.animals:
                    db.session.delete(animal)
            elif isinstance(user, User):
                # Cleanup specific to customers (e.g., delete cart, orders, etc.)
                if user.cart:
                    db.session.delete(user.cart)
                for order in user.orders:
                    db.session.delete(order)
                for payment in user.payments:
                    db.session.delete(payment)
            # No special cleanup required for Admin users in this example

            # Delete the user
            db.session.delete(user)
            db.session.commit()

            return {'message': f'User with ID {user_id} deleted successfully'}, 200

        except Exception as e:
            db.session.rollback()
            return {'error': f'An error occurred while deleting the user: {str(e)}'}, 500


api.add_resource(DeleteUserResource, '/users/<int:user_id>')



### AUTHENTICATION ###
class Login(Resource):
    def post(self):
       
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return make_response({"error": "Email and password are required"}, 400)

        # Attempt to find the user by email
        try:
            user = BaseUser.query.filter_by(email=email).first()

            if user and user.check_password(password):
                # Generate a JWT token
                token = jwt.encode(
                    {
                        "id": user.id,
                        "role": user.role,
                        "exp": datetime.utcnow() + timedelta(hours=24)
                    },
                    current_app.config['SECRET_KEY'],
                    algorithm="HS256"
                )

                # Log the user in
                login_user(user)

                return make_response({
                    "message": "Login successful",
                    "token": token,
                    "user": user.serialize()  # Return user details in response
                }, 200)

            return make_response({"error": "Invalid credentials"}, 401)

        except Exception as e:
            current_app.logger.error(f"Error during login: {str(e)}")
            return make_response({"error": "An internal error occurred"}, 500)

api.add_resource(Login, '/login')


class Logout(Resource):
    @login_required
    def post(self):
        try:
            logout_user()
            return make_response({"message": "Logout successful"}, 200)
        except Exception as e:
            current_app.logger.error(f"Error during logout: {str(e)}")
            return make_response({"error": "An internal error occurred"}, 500)

api.add_resource(Logout, '/logout')

class UserPatchResource(Resource):
    def patch(self, user_id):
        """Update user details by their ID."""
        user = User.query.get_or_404(user_id)
        data = request.get_json()

        # Validate and update fields if present in the request body
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            if not BaseUser.is_valid_email(data['email']):
                return {'error': 'Invalid email format'}, 400
            # Ensure the new email is not already in use
            existing_user = BaseUser.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user.id:
                return {'error': 'Email already in use'}, 400
            user.email = data['email']
        if 'role' in data:
            if data['role'] not in ['customer', 'admin']:
                return {'error': 'Invalid role specified'}, 400
            user.role = data['role']

        try:
            db.session.commit()
            return {'message': 'User updated successfully', 'user': user.serialize()}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'An error occurred while updating the user'}, 500


api.add_resource(UserPatchResource, '/users/<int:user_id>')

if __name__ == '__main__':
    app.run(debug=True)