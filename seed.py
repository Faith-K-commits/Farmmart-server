from config import db, app
from models import User, Vendor, Animal, Orders, OrderItem, Payments, Cart, CartItem
from datetime import datetime

def seed_users():
    """Seed the User model with initial data."""
    users = [
        {
            "name": "John Doe",
            "email": "john@example.com",
            "role": "customer",
            "password": "password123"
        },
        {
            "name": "Admin User",
            "email": "admin@example.com",
            "role": "admin",
            "password": "admin123"
        }
    ]

    for user_data in users:
        user = User(
            name=user_data["name"],
            email=user_data["email"],
            role=user_data["role"]
        )
        user.set_password(user_data["password"])
        db.session.add(user)

    db.session.commit()
    print("Users seeded successfully!")

def seed_vendors():
    """Seed the Vendor model with initial data."""
    vendors = [
        {
            "name": "Green Valley Farms",
            "email": "contact@greenvalley.com",
            "password": "vendor123",
            "phone_number": "123-456-7890",
            "farm_name": "Green Valley"
        },
        {
            "name": "Sunshine Ranch",
            "email": "info@sunshineranch.com",
            "password": "vendor456",
            "phone_number": "098-765-4321",
            "farm_name": "Sunshine Ranch"
        }
    ]

    for vendor_data in vendors:
        vendor = Vendor(
            name=vendor_data["name"],
            email=vendor_data["email"],
            phone_number=vendor_data["phone_number"],
            farm_name=vendor_data["farm_name"]
        )
        vendor.set_password(vendor_data["password"])  # Correctly set the password hash
        db.session.add(vendor)

    db.session.commit()
    print("Vendors seeded successfully!")

def seed_animals():
    """Seed the Animal model with initial data."""
    vendors = Vendor.query.all()
    if not vendors:
        print("No vendors found. Please seed vendors first.")
        return

    animals = [
        {
            "name": "Brown Cow",
            "price": 1500.0,
            "available_quantity": 10,
            "description": "A healthy brown cow for dairy production.",
            "category": "Cattle",
            "breed": "Holstein",
            "age": 5,
            "image_url": "https://example.com/images/brown-cow.jpg",
            "vendor_id": vendors[0].id
        },
        {
            "name": "Black Sheep",
            "price": 500.0,
            "available_quantity": 15,
            "description": "Young black sheep with soft wool.",
            "category": "Sheep",
            "breed": "Merino",
            "age": 2,
            "image_url": "https://example.com/images/black-sheep.jpg",
            "vendor_id": vendors[1].id
        }
    ]

    for animal_data in animals:
        animal = Animal(**animal_data)
        db.session.add(animal)

    db.session.commit()
    print("Animals seeded successfully!")

def seed_orders():
    """Seed the Orders model with initial data."""
    users = User.query.filter_by(role="customer").all()
    if not users:
        print("No users found. Please seed users first.")
        return

    orders = [
        {
            "user_id": users[0].id,
            "status": "Pending",
            "total_price": 2000.0
        }
    ]

    for order_data in orders:
        order = Orders(**order_data)
        db.session.add(order)

    db.session.commit()
    print("Orders seeded successfully!")

def seed_order_items():
    """Seed the OrderItem model with initial data."""
    orders = Orders.query.all()
    animals = Animal.query.all()

    if not orders or not animals:
        print("No orders or animals found. Please seed orders and animals first.")
        return

    order_items = [
        {
            "order_id": orders[0].id,
            "animal_id": animals[0].id,
            "quantity": 2,
            "unit_price": animals[0].price,
            "subtotal": animals[0].price * 2
        }
    ]

    for item_data in order_items:
        order_item = OrderItem(**item_data)
        db.session.add(order_item)

    db.session.commit()
    print("OrderItems seeded successfully!")

def seed_payments():
    """Seed the Payments model with initial data."""
    orders = Orders.query.all()
    users = User.query.filter_by(role="customer").all()

    if not orders or not users:
        print("No orders or users found. Please seed orders and users first.")
        return

    payments = [
        {
            "order_id": orders[0].id,
            "user_id": users[0].id,
            "amount": 2000.0,
            "status": "Completed"
        }
    ]

    for payment_data in payments:
        payment = Payments(**payment_data)
        db.session.add(payment)

    db.session.commit()
    print("Payments seeded successfully!")

def seed_cart():
    """Seed the Cart model with initial data."""
    users = User.query.filter_by(role="customer").all()

    if not users:
        print("No users found. Please seed users first.")
        return

    carts = [
        {
            "user_id": users[0].id
        }
    ]

    for cart_data in carts:
        cart = Cart(**cart_data)
        db.session.add(cart)

    db.session.commit()
    print("Carts seeded successfully!")

def seed_cart_items():
    """Seed the CartItem model with initial data."""
    carts = Cart.query.all()
    animals = Animal.query.all()

    if not carts or not animals:
        print("No carts or animals found. Please seed carts and animals first.")
        return

    cart_items = [
        {
            "cart_id": carts[0].id,
            "animal_id": animals[0].id,
            "quantity": 1
        }
    ]

    for item_data in cart_items:
        cart_item = CartItem(**item_data)
        db.session.add(cart_item)

    db.session.commit()
    print("CartItems seeded successfully!")

if __name__ == "__main__":
    with app.app_context():
        print("Seeding the database...")
        seed_users()
        seed_vendors()
        seed_animals()
        seed_orders()
        seed_order_items()
        seed_payments()
        seed_cart()
        seed_cart_items()
        print("Database seeding completed successfully!")
