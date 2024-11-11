from sqlalchemy_serializer import SerializerMixin
from config import db, bycrypt
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
import re  # For email validation

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='customer') 
    
    # Relationship to Cart
    cart = db.relationship('Cart', back_populates='user', uselist=False)
    
    # exclude password hash from serialization
    serialize_rules = ('-password_hash',)
    
    # Check constraint to ensure only specific roles are allowed
    __table_args__ = (
        CheckConstraint(role.in_(['admin', 'customer']), name='check_valid_role'),
    )

    def set_password(self, password):
        self.password_hash = bycrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bycrypt.check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    @staticmethod
    def is_valid_email(email):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    def __repr__(self):
        return f'<User {self.name}, Role {self.role}>'
    
class Animal(db.Model, SerializerMixin):
    __tablename__ = 'animals'

    # Primary Key: Unique identifier for each animal
    id = db.Column(db.Integer, primary_key=True)

    # Basic animal attributes
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    available_quantity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(50), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

    # Foreign Key linking to the Vendor (farmer) who listed the animal
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=True)  # Temporary Null value for testing

    # Relationship to Vendor model; allows access to the vendor's information from an animal instance
    vendor = db.relationship('Vendor', back_populates='animals')

    # Relationship to CartItem model; allows access to all cart items that include this animal
    # Useful for tracking demand and inventory across user carts
    cart_items = db.relationship('CartItem', back_populates='animal', lazy=True)

    def __repr__(self):
        return (f"<Animal(id={self.id}, name='{self.name}', category='{self.category}', breed='{self.breed}', age='{self.age}', price='{self.price}', image_url='{self.image_url}', vendor_id='{self.vendor_id}')>")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'available_quantity': self.available_quantity,
            'description': self.description,
            'category': self.category,
            'breed': self.breed,
            'age': self.age,
            'image_url': self.image_url,
            'vendor_id': self.vendor_id
        }

# Vendor model
class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)

    # Relationship to Animal model; allows access to all animals listed by the vendor
    animals = db.relationship('Animal', back_populates='vendor', lazy=True)

    def __repr__(self):
        return f"<Vendor(id={self.id}, name='{self.name}')>"



class Cart(db.Model):
    __tablename__ = 'carts'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Key linking to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Cart creation date
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last updated time

    # One-to-many relationship: A Cart can have many CartItems
    cart_items = db.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')

    # User relationship
    user = db.relationship('User', back_populates='cart')

    def __repr__(self):
        return f"<Cart user_id={self.user_id} created_at={self.created_at}>"

    def to_dict(self):
        # Serialize Cart to dictionary, including the CartItems and User info
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'cart_items': [item.to_dict() for item in self.cart_items],  # Serialize CartItems
            'user': self.user.to_dict()  # Serialize User info
        }
    

class CartItem(db.Model):
    __tablename__ = 'cart_items'  # table name in the database

    # Primary key: Unique identifier for each CartItem entry
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Key linking to the Cart table, represents the cart to which this item belongs
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)

    # Foreign Key linking to the Animal table, represents the animal product being added to the cart
    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id'), nullable=False)

    # Quantity of the animal product being added to the cart, default is 1
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # Timestamp of when the item was added to the cart, defaults to the current UTC time
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to the Cart model
    cart = db.relationship('Cart', back_populates='cart_items')

    # Relationship to the Animal model
    animal = db.relationship('Animal', back_populates='cart_items')

    def __repr__(self):
        """
        String representation of the CartItem instance, useful for debugging.
        Displays cart_id, animal_id, and quantity for easy identification.
        """
        return f"<CartItem cart_id={self.cart_id} animal_id={self.animal_id} quantity={self.quantity}>"

    def to_dict(self):
        """
        Serialize the CartItem instance to a dictionary format.
        Includes attributes such as id, cart_id, animal_id, quantity, added_at timestamp,
        and the associated animal details by calling animal.to_dict().
        """
        return {
            'id': self.id,
            'cart_id': self.cart_id,
            'animal_id': self.animal_id,
            'quantity': self.quantity,
            'added_at': self.added_at.isoformat(),
            'animal': self.animal.to_dict()  # Serialize the associated animal details
        }

