# import unittest
# from app import db, app
# from models import User, Cart, Vendor, Animal, Orders, OrderItem, CartItem, Payments

# class ModelRelationshipTest(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.app = app
#         cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Use a persistent test database
#         cls.app.config['TESTING'] = True
#         cls.app.app_context().push()
#         db.create_all()

#     @classmethod
#     def tearDownClass(cls):
#         db.session.remove()
#         db.drop_all()

#     def setUp(self):
#         db.session.begin_nested()

#     def tearDown(self):
#         db.session.rollback()

#     def test_user_cart_relationship(self):
#         user = User(name="Alice", email="alice@example.com", role="customer")
#         user.set_password("password123")
#         db.session.add(user)
#         db.session.commit()

#         cart = Cart(user_id=user.id)
#         db.session.add(cart)
#         db.session.commit()

#         self.assertEqual(user.cart.id, cart.id)
#         self.assertEqual(cart.user.id, user.id)

#     def test_vendor_animal_relationship(self):
#         vendor = Vendor(name="Farmer Bob", email="bob@example.com", phone_number="123-456-7890", farm_name="Bob's Farm")
#         vendor.set_password("securepassword")
#         db.session.add(vendor)
#         db.session.commit()

#         animal = Animal(name="Goat", price=150.0, category="Goat", available_quantity=10, vendor_id=vendor.id)
#         db.session.add(animal)
#         db.session.commit()

#         self.assertIn(animal, vendor.animals)
#         self.assertEqual(animal.vendor.id, vendor.id)

#     def test_order_orderitem_relationship(self):
#         user = User(name="Charlie", email="charlie@example.com", role="customer")
#         user.set_password("password123")
#         db.session.add(user)
#         db.session.commit()

#         order = Orders(user_id=user.id, total_price=300.0)
#         db.session.add(order)
#         db.session.commit()

#         animal = Animal(name="Pig", price=100.0, category="Pigs", available_quantity=5)

#         db.session.add(animal)
#         db.session.commit()

#         order_item = OrderItem(order_id=order.id, animal_id=animal.id, quantity=2, unit_price=100.0, subtotal=200.0)
#         db.session.add(order_item)
#         db.session.commit()

#         self.assertIn(order_item, order.order_items)
#         self.assertEqual(order_item.order.id, order.id)
#         self.assertEqual(order_item.animal.id, animal.id)

#     def test_cart_cartitem_relationship(self):
#         user = User(name="Dave", email="dave@example.com", role="customer")
#         user.set_password("password123")
#         db.session.add(user)
#         db.session.commit()

#         cart = Cart(user_id=user.id)
#         db.session.add(cart)
#         db.session.commit()

#         animal = Animal(name="Horse", price=500.0, category="Equine", available_quantity=3)
#         db.session.add(animal)
#         db.session.commit()

#         cart_item = CartItem(cart_id=cart.id, animal_id=animal.id, quantity=1)
#         db.session.add(cart_item)
#         db.session.commit()

#         self.assertIn(cart_item, cart.cart_items)
#         self.assertEqual(cart_item.cart.id, cart.id)
#         self.assertEqual(cart_item.animal.id, animal.id)

#     def test_user_orders_relationship(self):
#         user = User(name="Eve", email="eve@example.com", role="customer")
#         user.set_password("password123")
#         db.session.add(user)
#         db.session.commit()

#         order1 = Orders(user_id=user.id, total_price=500.0)
#         order2 = Orders(user_id=user.id, total_price=300.0)
#         db.session.add_all([order1, order2])
#         db.session.commit()

#         self.assertIn(order1, user.orders)
#         self.assertIn(order2, user.orders)

#     def test_order_payment_relationship(self):
#         user = User(name="Frank", email="frank@example.com", role="customer")
#         user.set_password("password123")
#         db.session.add(user)
#         db.session.commit()

#         order = Orders(user_id=user.id, total_price=400.0)
#         db.session.add(order)
#         db.session.commit()

#         payment = Payments(order_id=order.id, user_id=user.id, amount=400.0, status="Paid")
#         db.session.add(payment)
#         db.session.commit()

#         self.assertEqual(order.payment.id, payment.id)
#         self.assertEqual(payment.order.id, order.id)

# if __name__ == '__main__':
#     unittest.main()
