import unittest
from app import app, db  
from models import Vendor

class TestVendorModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  
        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.drop_all()

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.session.begin()

    def tearDown(self):
        db.session.rollback()
        self.app_context.pop()

    def test_create_vendor(self):
        vendor = Vendor(
            name="John Doe",
            email="johndoe@example.com",
            password="hashed_password"
        )
        db.session.add(vendor)
        db.session.commit()

        saved_vendor = Vendor.query.filter_by(email="johndoe@example.com").first()
        self.assertIsNotNone(saved_vendor)
        self.assertEqual(saved_vendor.name, "John Doe")
        self.assertEqual(saved_vendor.email, "johndoe@example.com")

    def test_vendor_repr(self):
        vendor = Vendor(
            name="Jane Smith",
            email="janesmith@example.com",
            password="hashed_password"
        )
        db.session.add(vendor)
        db.session.commit()

        # Test the __repr__ output with the expected format including None values
        self.assertEqual(
            repr(vendor),
            f"<Vendor(id={vendor.id}, name='Jane Smith', email='janesmith@example.com', phone_number='None', farm_name='None')>",
            "The __repr__ method should return a correctly formatted string."
        )

    def test_vendor_update(self):
        vendor = Vendor(
            name="Alex Johnson",
            email="alexj@example.com",
            password="hashed_password"
        )
        db.session.add(vendor)
        db.session.commit()

        vendor.email = "alexjohnson@example.com"
        db.session.commit()

        updated_vendor = Vendor.query.filter_by(name="Alex Johnson").first()
        self.assertEqual(updated_vendor.email, "alexjohnson@example.com")

    def test_required_fields(self):
        with self.assertRaises(Exception):
            vendor = Vendor(
                email="test@example.com",
                password="hashed_password"
            )
            db.session.add(vendor)
            db.session.commit()

    def test_serialization(self):
        vendor = Vendor(
            name="Samuel Jackson",
            email="samuelj@example.com",
            password="hashed_password"
        )
        db.session.add(vendor)
        db.session.commit()

        serialized_data = vendor.to_dict()
        self.assertIsInstance(serialized_data, dict)
        self.assertIn("name", serialized_data)
        self.assertIn("email", serialized_data)
        self.assertEqual(serialized_data["name"], "Samuel Jackson")
        self.assertEqual(serialized_data["email"], "samuelj@example.com")

if __name__ == "__main__":
    unittest.main()
