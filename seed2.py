from config import db, app
from models import User, Vendor, Animal, Orders, OrderItem, Payments, Cart, CartItem
from datetime import datetime

def clear_data():
    db.session.query(CartItem).delete()
    db.session.query(Cart).delete()
    db.session.query(OrderItem).delete()
    db.session.query(Orders).delete()
    db.session.query(Payments).delete()
    db.session.query(Animal).delete()
    db.session.query(Vendor).delete()
    db.session.query(User).delete()
    db.session.commit()
    print("Cleared existing data.")

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
    """Seed the Vendor model with 5 vendors."""
    vendors = [
        {
            "name": f"Vendor {i+1}",
            "email": f"vendor{i+1}@example.com",
            "password": f"vendor{i+1}password",
            "phone_number": f"555-123-000{i+1}",
            "farm_name": f"Farm {i+1}"
        }
        for i in range(5)
    ]

    for vendor_data in vendors:
        vendor = Vendor(
            name=vendor_data["name"],
            email=vendor_data["email"],
            phone_number=vendor_data["phone_number"],
            farm_name=vendor_data["farm_name"]
        )
        vendor.set_password(vendor_data["password"])  # Hash the password
        db.session.add(vendor)

    db.session.commit()
    print("5 Vendors seeded successfully!")

def seed_animals():
    """Seed the Animal model with 3 animals per vendor."""
    vendors = Vendor.query.all()
    if not vendors:
        print("No vendors found. Please seed vendors first.")
        return

    animal_templates = [
        {
            "name": "Brown Cow",
            "price": 1500.0,
            "available_quantity": 10,
            "description": "A healthy brown cow for dairy production.",
            "category": "Cattle",
            "breed": "Holstein",
            "age": 5,
            "image_url": "https://example.com/images/brown-cow.jpg"
        },
        {
            "name": "Black Sheep",
            "price": 500.0,
            "available_quantity": 15,
            "description": "Young black sheep with soft wool.",
            "category": "Sheep",
            "breed": "Merino",
            "age": 2,
            "image_url": "https://example.com/images/black-sheep.jpg"
        },
        {
            "name": "White Goat",
            "price": 700.0,
            "available_quantity": 8,
            "description": "A playful white goat, perfect for grazing.",
            "category": "Goat",
            "breed": "Saanen",
            "age": 3,
            "image_url": "https://example.com/images/white-goat.jpg"
        }
    ]

    for vendor in vendors:
        for template in animal_templates:
            # Copy template data and assign it to the current vendor
            animal_data = {**template, "vendor_id": vendor.id}
            animal = Animal(**animal_data)
            db.session.add(animal)

    db.session.commit()
    print("3 animals per vendor seeded successfully!")

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
            "status": "Paid"
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
        clear_data()
        seed_users()
        seed_vendors()
        seed_animals()
        seed_orders()
        seed_order_items()
        seed_payments()
        seed_cart()
        seed_cart_items()
        print("Database seeding completed successfully!")
