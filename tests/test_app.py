import unittest
import os
from app import app, db 

class BasicTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///:memory:')
        cls.client = app.test_client()
        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), 'Welcome to the Home Page')
        
    def test_ci(self):
        response = self.client.get('/ci')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), 'Welcome to the CI/CD with Github Actions')

if __name__ == "__main__":
    unittest.main()