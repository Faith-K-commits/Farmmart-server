import unittest
from config import db, app
from models import Animal

class TestAnimalModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Runs once before all tests.
        Sets up the application context and initializes the database tables.
        """
        app.config['TESTING'] = True
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

    def test_create_animal(self):
        """
        Tests the creation of an Animal instance in the database.
        - Adds a new animal to the database.
        - Verifies that the animal was saved and that its fields are correct.
        """
        animal = Animal(
            name="Test Cow",
            price=1500.0,
            available_quantity=10,
            description="Sample description",
            category="Cattle",
            breed="Holstein",
            age=5,
            image_url="http://example.com/test-cow.jpg"
        )
        db.session.add(animal)
        db.session.commit()

        # Retrieve from DB and assert values
        saved_animal = Animal.query.filter_by(name="Test Cow").first()
        self.assertIsNotNone(saved_animal, "Animal should be saved in the database.")
        self.assertEqual(saved_animal.price, 1500.0, "Animal price should be 1500.0")
        self.assertEqual(saved_animal.category, "Cattle", "Animal category should be 'Cattle'")

    def test_animal_repr(self):
        """
        Tests the __repr__ method of the Animal model.
        - Creates a sample animal and verifies the returned string representation.
        """
        animal = Animal(
            name="Test Cow",
            price=1500.0,
            available_quantity=10,
            description="Sample description",
            category="Cattle",
            breed="Holstein",
            age=5,
            image_url="http://example.com/test-cow.jpg"
        )
        db.session.add(animal)
        db.session.commit()

        # Test if the __repr__ output is formatted as expected
        self.assertEqual(
            repr(animal),
            "<Animal(id={}, name='Test Cow', category='Cattle', breed='Holstein', age='5', price='1500.0', image_url='http://example.com/test-cow.jpg', vendor_id='None')>".format(animal.id),
            "The __repr__ method should return a correctly formatted string."
        )

    def test_animal_update(self):
        """
        Tests updating an Animal instance in the database.
        - Creates a sample animal, updates its price and quantity, and saves changes.
        - Verifies the updated values in the database.
        """
        animal = Animal(
            name="Test Goat",
            price=300.0,
            available_quantity=5,
            description="Test description",
            category="Goats",
            breed="Alpine",
            age=2,
            image_url="http://example.com/test-goat.jpg"
        )
        db.session.add(animal)
        db.session.commit()

        # Update the price and quantity
        animal.price = 350.0
        animal.available_quantity = 10
        db.session.commit()

        # Retrieve the updated animal and verify new values
        updated_animal = Animal.query.filter_by(name="Test Goat").first()
        self.assertEqual(updated_animal.price, 350.0, "Updated price should be 350.0")
        self.assertEqual(updated_animal.available_quantity, 10, "Updated quantity should be 10")

    def test_required_fields(self):
        """
        Tests that required fields are enforced by the Animal model.
        - Attempts to create an animal without the required `name` field.
        - Expects an exception due to the missing required field.
        """
        with self.assertRaises(Exception, msg="Creating an Animal without required fields should raise an exception"):
            animal = Animal(
                price=200.0,
                available_quantity=3,
                category="Poultry"
            )
            db.session.add(animal)
            db.session.commit()

    def test_serialization(self):
        """
        Tests the to_dict serialization method provided by SerializerMixin.
        - Serializes an Animal instance to a dictionary.
        - Verifies that the dictionary contains the correct keys and values.
        """
        animal = Animal(
            name="Test Sheep",
            price=600.0,
            available_quantity=7,
            description="Healthy sheep",
            category="Sheep",
            breed="Merino",
            age=3,
            image_url="http://example.com/test-sheep.jpg"
        )
        db.session.add(animal)
        db.session.commit()

        # Serialize the animal and verify content
        serialized_data = animal.to_dict()
        self.assertIsInstance(serialized_data, dict, "Serialization should return a dictionary.")
        self.assertIn("name", serialized_data, "Serialized data should contain 'name' key.")
        self.assertIn("price", serialized_data, "Serialized data should contain 'price' key.")
        self.assertEqual(serialized_data["name"], "Test Sheep", "Name in serialized data should match original.")
        self.assertEqual(serialized_data["price"], 600.0, "Price in serialized data should match original.")

if __name__ == "__main__":
    unittest.main()
