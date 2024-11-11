# import unittest
# from datetime import datetime
# from config import db, app
# from models import User, Animal, Cart, CartItem
# import uuid

# class TestCartModel(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         """Set up the application context and initialize the database tables."""
#         app.config['TESTING'] = True
#         with app.app_context():
#             db.create_all()

#     @classmethod
#     def tearDownClass(cls):
#         """Clean up the database by dropping all tables after all tests."""
#         with app.app_context():
#             db.drop_all()

#     def setUp(self):
#         """Start a new application context and begin a session for each test."""
#         self.app_context = app.app_context()
#         self.app_context.push()
#         db.session.begin()

#         # Create a unique email for each test user
#         unique_email = f"testuser-{uuid.uuid4()}@example.com"
        
#         # Set up test user and animal
#         self.user = User(name="Test User", email=unique_email)
#         self.user.set_password("password")
#         db.session.add(self.user)

#         self.animal = Animal(
#             name="Test Cow",
#             price=1500.0,
#             available_quantity=10,
#             description="Healthy cow",
#             category="Cattle",
#             breed="Holstein",
#             age=5,
#             image_url="http://example.com/test-cow.jpg"
#         )
#         db.session.add(self.animal)
#         db.session.commit()

#     def tearDown(self):
#         """Roll back any database changes and end the application context."""
#         db.session.rollback()
#         self.app_context.pop()

#     def test_create_cart(self):
#         """Test creating a Cart instance for a user."""
#         cart = Cart(user_id=self.user.id)
#         db.session.add(cart)
#         db.session.commit()

#         saved_cart = Cart.query.filter_by(user_id=self.user.id).first()
#         self.assertIsNotNone(saved_cart, "Cart should be saved in the database.")
#         self.assertEqual(saved_cart.user_id, self.user.id, "Cart user_id should match the User's id.")

#     def test_add_item_to_cart(self):
#         """Test adding an item to a user's cart."""
#         cart = Cart(user_id=self.user.id)
#         db.session.add(cart)
#         db.session.commit()

#         cart_item = CartItem(cart_id=cart.id, animal_id=self.animal.id, quantity=2)
#         db.session.add(cart_item)
#         db.session.commit()

#         saved_cart_item = CartItem.query.filter_by(cart_id=cart.id).first()
#         self.assertIsNotNone(saved_cart_item, "CartItem should be saved in the database.")
#         self.assertEqual(saved_cart_item.quantity, 2, "Quantity of CartItem should be 2.")
#         self.assertEqual(saved_cart_item.animal_id, self.animal.id, "CartItem animal_id should match the Animal's id.")

#     def test_cart_item_relationship(self):
#         """Test that CartItem relationships are correctly set up."""
#         cart = Cart(user_id=self.user.id)
#         db.session.add(cart)
#         db.session.commit()

#         cart_item = CartItem(cart_id=cart.id, animal_id=self.animal.id, quantity=1)
#         db.session.add(cart_item)
#         db.session.commit()

#         saved_cart = Cart.query.get(cart.id)
#         saved_animal = Animal.query.get(self.animal.id)

#         self.assertIn(cart_item, saved_cart.cart_items, "Cart should include the added CartItem.")
#         self.assertEqual(cart_item.animal, saved_animal, "CartItem should link to the correct Animal.")

#     def test_update_cart_item_quantity(self):
#         """Test updating the quantity of an item in the cart."""
#         cart = Cart(user_id=self.user.id)
#         db.session.add(cart)
#         db.session.commit()

#         cart_item = CartItem(cart_id=cart.id, animal_id=self.animal.id, quantity=1)
#         db.session.add(cart_item)
#         db.session.commit()

#         # Update quantity and save
#         cart_item.quantity = 3
#         db.session.commit()

#         updated_cart_item = CartItem.query.get(cart_item.id)
#         self.assertEqual(updated_cart_item.quantity, 3, "Updated CartItem quantity should be 3.")

#     def test_cart_total_items(self):
#         """Test the total quantity of items in the cart."""
#         cart = Cart(user_id=self.user.id)
#         db.session.add(cart)
#         db.session.commit()

#         cart_item1 = CartItem(cart_id=cart.id, animal_id=self.animal.id, quantity=2)
#         db.session.add(cart_item1)

#         # Add another animal
#         another_animal = Animal(
#             name="Test Goat",
#             price=500.0,
#             available_quantity=8,
#             category="Goats",
#             breed="Alpine",
#             age=3,
#             image_url="http://example.com/test-goat.jpg"
#         )
#         db.session.add(another_animal)
#         db.session.commit()

#         cart_item2 = CartItem(cart_id=cart.id, animal_id=another_animal.id, quantity=3)
#         db.session.add(cart_item2)
#         db.session.commit()

#         total_quantity = sum(item.quantity for item in cart.cart_items)
#         self.assertEqual(total_quantity, 5, "Total quantity of items in the cart should be 5.")

#     def test_delete_cart_item(self):
#         """Test removing an item from the cart."""
#         cart = Cart(user_id=self.user.id)
#         db.session.add(cart)
#         db.session.commit()

#         cart_item = CartItem(cart_id=cart.id, animal_id=self.animal.id, quantity=1)
#         db.session.add(cart_item)
#         db.session.commit()

#         db.session.delete(cart_item)
#         db.session.commit()

#         deleted_item = CartItem.query.get(cart_item.id)
#         self.assertIsNone(deleted_item, "CartItem should be deleted from the database.")

# if __name__ == "__main__":
#     unittest.main()
import unittest
from datetime import datetime
from config import db, app
from models import User, Animal, Cart, CartItem
import uuid

class TestCartModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the application context and initialize the database tables."""
        app.config['TESTING'] = True  # Enable testing configuration for the app
        with app.app_context():
            db.create_all()  # Create all tables before any tests run

    @classmethod
    def tearDownClass(cls):
        """Clean up the database by dropping all tables after all tests."""
        with app.app_context():
            db.drop_all()  # Drop all tables to ensure a clean slate after tests

    def setUp(self):
        """Start a new application context and begin a session for each test."""
        # Set up the application context for testing
        self.app_context = app.app_context()
        self.app_context.push()
        db.session.begin()  # Start a new database session for each test

        # Create a unique email for each test user
        unique_email = f"testuser-{uuid.uuid4()}@example.com"
        
        # Set up a test user and add them to the session
        self.user = User(name="Test User", email=unique_email)
        self.user.set_password("password")  # Set a password for the user
        db.session.add(self.user)

        # Set up a test animal and add it to the session
        self.animal = Animal(
            name="Test Cow",
            price=1500.0,
            available_quantity=10,
            description="Healthy cow",
            category="Cattle",
            breed="Holstein",
            age=5,
            image_url="http://example.com/test-cow.jpg"
        )
        db.session.add(self.animal)
        db.session.commit()  # Commit the user and animal to the database

    def tearDown(self):
        """Roll back any database changes and end the application context."""
        db.session.rollback()  # Undo any changes made during the test
        self.app_context.pop()  # Remove the application context

    def test_create_cart(self):
        """Test creating a Cart instance for a user."""
        # Create and save a cart associated with the test user
        cart = Cart(user_id=self.user.id)
        db.session.add(cart)
        db.session.commit()

        # Retrieve the saved cart and verify it exists
        saved_cart = db.session.get(Cart, cart.id)
        self.assertIsNotNone(saved_cart, "Cart should be saved in the database.")
        self.assertEqual(saved_cart.user_id, self.user.id, "Cart user_id should match the User's id.")

    def test_add_item_to_cart(self):
        """Test adding an item to a user's cart."""
        # Create and save a cart for the user
        cart = Cart(user_id=self.user.id)
        db.session.add(cart)
        db.session.commit()

        # Create a CartItem linking the cart and the animal, then save it
        cart_item = CartItem(cart_id=cart.id, animal_id=self.animal.id, quantity=2)
        db.session.add(cart_item)
        db.session.commit()

        # Retrieve the saved cart item and check its attributes
        saved_cart_item = db.session.get(CartItem, cart_item.id)
        self.assertIsNotNone(saved_cart_item, "CartItem should be saved in the database.")
        self.assertEqual(saved_cart_item.quantity, 2, "Quantity of CartItem should be 2.")
        self.assertEqual(saved_cart_item.animal_id, self.animal.id, "CartItem animal_id should match the Animal's id.")

    def test_cart_item_relationship(self):
        """Test that CartItem relationships are correctly set up."""
        # Create and save a cart for the user
        cart = Cart(user_id=self.user.id)
        db.session.add(cart)
        db.session.commit()

        # Create a CartItem linking the cart and the animal, then save it
        cart_item = CartItem(cart_id=cart.id, animal_id=self.animal.id, quantity=1)
        db.session.add(cart_item)
        db.session.commit()

        # Retrieve the saved cart and animal using the session, and verify relationships
        saved_cart = db.session.get(Cart, cart.id)
        saved_animal = db.session.get(Animal, self.animal.id)

        self.assertIn(cart_item, saved_cart.cart_items, "Cart should include the added CartItem.")
        self.assertEqual(cart_item.animal, saved_animal, "CartItem should link to the correct Animal.")

    def test_update_cart_item_quantity(self):
        """Test updating the quantity of an item in the cart."""
        # Create and save a cart and CartItem
        cart = Cart(user_id=self.user.id)
        db.session.add(cart)
        db.session.commit()

        cart_item = CartItem(cart_id=cart.id, animal_id=self.animal.id, quantity=1)
        db.session.add(cart_item)
        db.session.commit()

        # Update CartItem quantity and commit the change
        cart_item.quantity = 3
        db.session.commit()

        # Retrieve the updated CartItem and verify the quantity was updated
        updated_cart_item = db.session.get(CartItem, cart_item.id)
        self.assertEqual(updated_cart_item.quantity, 3, "Updated CartItem quantity should be 3.")

    def test_cart_total_items(self):
        """Test the total quantity of items in the cart."""
        # Create and save a cart for the user
        cart = Cart(user_id=self.user.id)
        db.session.add(cart)
        db.session.commit()

        # Add two CartItems to the cart with different animals and quantities
        cart_item1 = CartItem(cart_id=cart.id, animal_id=self.animal.id, quantity=2)
        db.session.add(cart_item1)

        # Create and save another animal for a new CartItem
        another_animal = Animal(
            name="Test Goat",
            price=500.0,
            available_quantity=8,
            category="Goats",
            breed="Alpine",
            age=3,
            image_url="http://example.com/test-goat.jpg"
        )
        db.session.add(another_animal)
        db.session.commit()

        # Add a second CartItem to the cart
        cart_item2 = CartItem(cart_id=cart.id, animal_id=another_animal.id, quantity=3)
        db.session.add(cart_item2)
        db.session.commit()

        # Calculate total quantity of items in the cart
        total_quantity = sum(item.quantity for item in cart.cart_items)
        self.assertEqual(total_quantity, 5, "Total quantity of items in the cart should be 5.")

    def test_delete_cart_item(self):
        """Test removing an item from the cart."""
        # Create and save a cart and CartItem
        cart = Cart(user_id=self.user.id)
        db.session.add(cart)
        db.session.commit()

        cart_item = CartItem(cart_id=cart.id, animal_id=self.animal.id, quantity=1)
        db.session.add(cart_item)
        db.session.commit()

        # Delete the CartItem and commit the change
        db.session.delete(cart_item)
        db.session.commit()

        # Verify the CartItem has been deleted from the database
        deleted_item = db.session.get(CartItem, cart_item.id)
        self.assertIsNone(deleted_item, "CartItem should be deleted from the database.")

if __name__ == "__main__":
    unittest.main()
