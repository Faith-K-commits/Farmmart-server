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

# Register the UploadImage resource with the API
api.add_resource(UploadImage, '/upload')

if __name__ == '__main__':
    app.run(debug=True)