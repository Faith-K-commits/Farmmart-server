from flask import make_response, jsonify, request
from flask_restful import Resource
from config import db, app, api
from models import Animal, User
# import cloudinary.uploader

# Secret key for sessions
app.config['SECRET_KEY'] = 'secret_key'

@app.route('/')
def home():
    return 'Welcome to the Home Page'

@app.route('/ci')
def ci():
    return 'Welcome to the CI/CD with Github Actions'

# # Resource for uploading images to Cloudinary (Testing if cloudinary is available and functioning properly)
# class UploadImage(Resource):
#     def post(self):
#         # Check if a file part is in the request
#         if 'file' not in request.files:
#             return {"error": "No file part in the request"}, 400

#         file = request.files['file']

#         # Ensure the file is not empty
#         if file.filename == '':
#             return {"error": "No file selected for uploading"}, 400

#         try:
#             # Upload the file to Cloudinary and retrieve the result
#             result = cloudinary.uploader.upload(file)
#             # Return the URL of the uploaded image as JSON
#             return {"url": result['secure_url']}, 200
#         except Exception as e:
#             # Handle any exceptions and return an error message
#             return {"error": str(e)}, 500

# # Register the UploadImage resource with the API
# api.add_resource(UploadImage, '/upload')

class RegisterResource(Resource):
    def post(self):
        data = request.get_json()

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'customer')#default to customer if not provided

        if not all([name, email, password]):
            return{'error': 'Name, Email and password required'}, 400

        if not User.is_valid_email(email):
            return {'error': 'Enter a valid Email'}, 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {'error': 'Email already in use'}

        new_user = User(name=name, email=email, role=role)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            return {'message': 'User created successfully', 'user': new_user.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            return {'error': 'An error occurred while creating the user'}, 500

        return {'message': 'User registered successfully', 'user': new_user.to_dict()}, 201

api.add_resource(RegisterResource, '/register')


class UserListResource(Resource):
    def get(self):
        """Fetches paginated users."""
        page = request.args.get('page', 1, type=int)  # Default to page 1
        per_page = request.args.get('per_page', 10, type=int)  # Default to 10 users per page

        paginated_users = User.query.paginate(page=page, per_page=per_page, error_out=False)
        users = [user.to_dict() for user in paginated_users.items]

        return {
            'users': users,
            'total': paginated_users.total,
            'pages': paginated_users.pages,
            'current_page': paginated_users.page,
            'per_page': paginated_users.per_page
        }, 200

api.add_resource(UserListResource, '/users' )

class DeleteUserResource(Resource):
    def delete(self, user_id):
        """Deletes a user by their ID."""
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        try:
            db.session.delete(user)
            db.session.commit()
            return {'message': 'User deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'An error occurred while deleting the user'}, 500

api.add_resource(DeleteUserResource, '/users/<int:user_id>' )


if __name__ == '__main__':
    app.run(debug=True)