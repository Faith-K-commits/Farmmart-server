import unittest
from app import app, db  
from models import Vendor

class TestVendorModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Runs once before all tests.
        Sets up the application context and initializes the database tables.
        """
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  
        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        """
        Runs once after all tests.
        Drops all tables to clean up the database.
        """
        with app.app_context():
            db.drop_all()

    def setUp(self):
        """
        Runs before each individual test.
        Starts an application context and begins a new session for database transactions.
        """
        self.app_context = app.app_context()
        self.app_context.push()
        db.session.begin()

    def tearDown(self):
        """
        Runs after each individual test.
        Rolls back any changes made to the database and ends the application context.
        """
        db.session.rollback()
        self.app_context.pop()

    def test_create_vendor(self):
        """
        Tests the creation of a Vendor instance in the database.
        - Adds a new vendor to the database.
        - Verifies that the vendor was saved and that its fields are correct.
        """
        vendor = Vendor(
            name="John Doe",
            email="johndoe@example.com",
            password="hashed_password"
        )
        db.session.add(vendor)
        db.session.commit()

        # Retrieve from DB and assert values
        saved_vendor = Vendor.query.filter_by(email="johndoe@example.com").first()
        self.assertIsNotNone(saved_vendor, "Vendor should be saved in the database.")
        self.assertEqual(saved_vendor.name, "John Doe", "Vendor name should be 'John Doe'")
        self.assertEqual(saved_vendor.email, "johndoe@example.com", "Vendor email should be 'johndoe@example.com'")

    def test_vendor_repr(self):
        """
        Tests the __repr__ method of the Vendor model.
        - Creates a sample vendor and verifies the returned string representation.
        """
        vendor = Vendor(
            name="Jane Smith",
            email="janesmith@example.com",
            password="hashed_password"
        )
        db.session.add(vendor)
        db.session.commit()

        # Test if the __repr__ output is formatted as expected
        self.assertEqual(
            repr(vendor),
            f"<Vendor(id={vendor.id}, name='Jane Smith', email='janesmith@example.com')>",
            "The __repr__ method should return a correctly formatted string."
        )

    def test_vendor_update(self):
        """
        Tests updating a Vendor instance in the database.
        - Creates a sample vendor, updates its email, and saves changes.
        - Verifies the updated values in the database.
        """
        vendor = Vendor(
            name="Alex Johnson",
            email="alexj@example.com",
            password="hashed_password"
        )
        db.session.add(vendor)
        db.session.commit()

        # Update the email
        vendor.email = "alexjohnson@example.com"
        db.session.commit()

        # Retrieve the updated vendor and verify new email
        updated_vendor = Vendor.query.filter_by(name="Alex Johnson").first()
        self.assertEqual(updated_vendor.email, "alexjohnson@example.com", "Updated email should be 'alexjohnson@example.com'")

    def test_required_fields(self):
        """
        Tests that required fields are enforced by the Vendor model.
        - Attempts to create a vendor without the required `name` field.
        - Expects an exception due to the missing required field.
        """
        with self.assertRaises(Exception, msg="Creating a Vendor without required fields should raise an exception"):
            vendor = Vendor(
                email="test@example.com",
                password="hashed_password"
            )
            db.session.add(vendor)
            db.session.commit()

    def test_serialization(self):
        """
        Tests the to_dict serialization method provided by SerializerMixin.
        - Serializes a Vendor instance to a dictionary.
        - Verifies that the dictionary contains the correct keys and values.
        """
        vendor = Vendor(
            name="Samuel Jackson",
            email="samuelj@example.com",
            password="hashed_password"
        )
        db.session.add(vendor)
        db.session.commit()

        # Serialize the vendor and verify content
        serialized_data = vendor.to_dict()
        self.assertIsInstance(serialized_data, dict, "Serialization should return a dictionary.")
        self.assertIn("name", serialized_data, "Serialized data should contain 'name' key.")
        self.assertIn("email", serialized_data, "Serialized data should contain 'email' key.")
        self.assertEqual(serialized_data["name"], "Samuel Jackson", "Name in serialized data should match original.")
        self.assertEqual(serialized_data["email"], "samuelj@example.com", "Email in serialized data should match original.")

if __name__ == "__main__":
    unittest.main()
