from flask import make_response, jsonify, request
from flask_restful import Resource
from config import db, app, api
from models import Animal
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
        
# Resource for CRUD operations on Animal entities
class AnimalResource(Resource):
    
    # GET method to retrieve animals
    def get(self, animal_id=None):
        if animal_id:
            # Fetch a single animal by ID
            animal = db.session.get(Animal, animal_id)
            if not animal:
                return make_response(jsonify({"error": "No animal found with this ID!"}), 404)
            return make_response(jsonify(self.serialize_animal(animal)), 200)
        
        # Pagination: retrieve 'page' and 'per_page' from query parameters, with defaults
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        try:
            # Query and paginate animals, based on requested page and per_page
            animals_query = Animal.query.paginate(page=page, per_page=per_page, error_out=False)
            
            # Serialize the animals on the current page
            animals = [self.serialize_animal(animal) for animal in animals_query.items]
            
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
            return make_response(jsonify(self.serialize_animal(animal)), 201)
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
            return make_response(jsonify(self.serialize_animal(animal)), 200)
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
    
    # Helper method to serialize an animal instance without recursion
    def serialize_animal(self, animal):
        return {
            "id": animal.id,
            "name": animal.name,
            "price": animal.price,
            "available_quantity": animal.available_quantity,
            "description": animal.description,
            "category": animal.category,
            "breed": animal.breed,
            "age": animal.age,
            "image_url": animal.image_url,
            "vendor_id": animal.vendor_id
        }

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
        animals = [self.serialize_animal(animal) for animal in animals_query.items]

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

    def serialize_animal(self, animal):
        return {
            "id": animal.id,
            "name": animal.name,
            "price": animal.price,
            "available_quantity": animal.available_quantity,
            "description": animal.description,
            "category": animal.category,
            "breed": animal.breed,
            "age": animal.age,
            "image_url": animal.image_url,
            "vendor_id": animal.vendor_id
        }

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
        animals = [self.serialize_animal(animal) for animal in animals_query.items]

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

    def serialize_animal(self, animal):
        return {
            "id": animal.id,
            "name": animal.name,
            "price": animal.price,
            "available_quantity": animal.available_quantity,
            "description": animal.description,
            "category": animal.category,
            "breed": animal.breed,
            "age": animal.age,
            "image_url": animal.image_url,
            "vendor_id": animal.vendor_id
        }
    
# Register the resource with the API
api.add_resource(UploadImage, '/upload')
api.add_resource(AnimalResource, '/animals', '/animals/<int:animal_id>')
api.add_resource(AnimalSearchResource, '/animals/search')
api.add_resource(AnimalFilterResource, '/animals/filter')

if __name__ == '__main__':
    app.run(debug=True)