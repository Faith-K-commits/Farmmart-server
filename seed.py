from config import db, app
from models import BaseUser, Animal, Orders, OrderItem, Payments, Cart, CartItem
from datetime import datetime

def clear_data():
    """Clear all data from the database."""
    db.session.query(CartItem).delete()
    db.session.query(Cart).delete()
    db.session.query(OrderItem).delete()
    db.session.query(Orders).delete()
    db.session.query(Payments).delete()
    db.session.query(Animal).delete()
    db.session.query(BaseUser).delete()
    db.session.commit()
    print("Cleared existing data.")

def seed_users_and_vendors():
    """Seed BaseUser model with both user and vendor data."""
    users_and_vendors = [
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
        },
        {
            "name": "Vendor 1",
            "email": "vendor1@example.com",
            "role": "vendor",
            "password": "vendor1password",
            "phone_number": "555-123-0001",
            "farm_name": "Farm 1"
        },
        {
            "name": "Vendor 2",
            "email": "vendor2@example.com",
            "role": "vendor",
            "password": "vendor2password",
            "phone_number": "555-123-0002",
            "farm_name": "Farm 2"
        },
    ]

    for user_data in users_and_vendors:
        user = BaseUser(
            name=user_data["name"],
            email=user_data["email"],
            role=user_data["role"]
        )
        user.set_password(user_data["password"])
        if user.role == "vendor":
            user.phone_number = user_data["phone_number"]
            user.farm_name = user_data["farm_name"]
        db.session.add(user)

    db.session.commit()
    print("Users and Vendors seeded successfully!")

def seed_animals():
    """Seed the Animal model with animals associated with vendors."""
    vendors = BaseUser.query.filter_by(role="vendor").all()
    if not vendors:
        print("No vendors found. Please seed vendors first.")
        return

    animal_templates = [
        {
            "name": "Friesian Cow",
            "price": 260000.0,
            "available_quantity": 10,
            "description": "A healthy female black and white cow for dairy production.",
            "category": "Cattle",
            "breed": "Holstein Friesian",
            "age": 5,
            "image_url": "https://res.cloudinary.com/dukxm7ilt/image/upload/v1731665187/plb4v7ksb8ckr2g5xqtt.jpg"
        },
        {
            "name": "White Sheep",
            "price": 30000.0,
            "available_quantity": 15,
            "description": "Young white sheep with soft wool.",
            "category": "Sheep",
            "breed": "Merino",
            "age": 2,
            "image_url": "https://res.cloudinary.com/dukxm7ilt/image/upload/v1731665412/vzplzy8uhxufuubpzeuj.jpg"
        },
        {
            "name": "White Goat",
            "price": 25000.0,
            "available_quantity": 8,
            "description": "A playful white goat, perfect for grazing and milking.",
            "category": "Goat",
            "breed": "Saanen",
            "age": 3,
            "image_url": "https://res.cloudinary.com/dukxm7ilt/image/upload/v1731665974/ghpf0zct2ac6awdsrd2f.jpg"
        }
    ]

    for vendor in vendors:
        for template in animal_templates:
            animal = Animal(**template, user_id=vendor.id)
            db.session.add(animal)

    db.session.commit()
    print("Animals seeded successfully!")

def seed_carts():
    """Seed the Cart model with carts for customers."""
    customers = BaseUser.query.filter_by(role="customer").all()
    if not customers:
        print("No customers found. Please seed users first.")
        return

    for customer in customers:
        cart = Cart(user_id=customer.id)
        db.session.add(cart)

    db.session.commit()
    print("Carts seeded successfully!")

def seed_cart_items():
    """Seed the CartItem model with items in the carts."""
    carts = Cart.query.all()
    animals = Animal.query.all()

    if not carts or not animals:
        print("No carts or animals found. Please seed carts and animals first.")
        return

    cart_items = [
        {
            "cart_id": carts[0].id,
            "animal_id": animals[0].id,
            "quantity": 2
        },
        {
            "cart_id": carts[0].id,
            "animal_id": animals[1].id,
            "quantity": 1
        }
    ]

    for item_data in cart_items:
        cart_item = CartItem(**item_data)
        db.session.add(cart_item)

    db.session.commit()
    print("CartItems seeded successfully!")

def seed_orders():
    """Seed the Orders model with orders for customers."""
    customers = BaseUser.query.filter_by(role="customer").all()
    if not customers:
        print("No customers found. Please seed users first.")
        return

    orders = [
        {
            "user_id": customers[0].id,
            "status": "Pending",
            "total_price": 60000.0,
        }
    ]

    for order_data in orders:
        order = Orders(**order_data)
        db.session.add(order)

    db.session.commit()
    print("Orders seeded successfully!")

def seed_order_items():
    """Seed the OrderItem model with items in the orders."""
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
        },
        {
            "order_id": orders[0].id,
            "animal_id": animals[1].id,
            "quantity": 1,
            "unit_price": animals[1].price,
            "subtotal": animals[1].price
        }
    ]

    for item_data in order_items:
        order_item = OrderItem(**item_data)
        db.session.add(order_item)

    db.session.commit()
    print("OrderItems seeded successfully!")

def seed_payments():
    """Seed the Payments model with payments for orders."""
    orders = Orders.query.all()
    customers = BaseUser.query.filter_by(role="customer").all()

    if not orders or not customers:
        print("No orders or customers found. Please seed orders and users first.")
        return

    payments = [
        {
            "order_id": orders[0].id,
            "user_id": customers[0].id,
            "amount": 60000.0,
            "status": "Paid"
        }
    ]

    for payment_data in payments:
        payment = Payments(**payment_data)
        db.session.add(payment)

    db.session.commit()
    print("Payments seeded successfully!")

if __name__ == "__main__":
    with app.app_context():
        print("Seeding the database...")
        clear_data()
        seed_users_and_vendors()
        seed_animals()
        seed_carts()
        seed_cart_items()
        seed_orders()
        seed_order_items()
        seed_payments()
        print("Database seeding completed successfully!")
