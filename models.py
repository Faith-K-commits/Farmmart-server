from sqlalchemy_serializer import SerializerMixin
from config import db, bycrypt
from sqlalchemy.orm import relationship
from datetime import datetime

# Animal model: represents animals listed for sale by vendors.
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

    # # Foreign Key linking to the Vendor (farmer) who listed the animal
    # vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=True) #Temporary Null value for testing (Remember to change this when vendor model is ready)

    # # Relationship to Vendor model; allows access to the vendor's information from an animal instance
    # vendor = db.relationship('Vendor', back_populates='animals')

    # # Relationship to CartItem model; allows access to all cart items that include this animal
    # # Useful for tracking demand and inventory across user carts
    cart_items = db.relationship('CartItem', back_populates='animal', lazy=True)

    def __repr__(self):
        return (f"<Animal(id={self.id}, name='{self.name}', category='{self.category}', breed='{self.breed}', age='{self.age}', price='{self.price}', image_url='{self.image_url}', vendor_id='{self.vendor_id}')>")
    
class Cart(db.Model):
    __tablename__ = 'carts'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Key linking to User
    #user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Cart creation date
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last updated time

    # One-to-many relationship: A Cart can have many CartItems
    cart_items = db.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')

    # User relationship
    #user = db.relationship('User', back_populates='cart')

    # def __repr__(self):
    #     return f"<Cart user_id={self.user_id} created_at={self.created_at}>"

    def to_dict(self):
        # Serialize Cart to dictionary, including the CartItems and User info
        return {
            'id': self.id,
            #'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'cart_items': [item.to_dict() for item in self.cart_items],  # Serialize CartItems
            #'user': self.user.to_dict()  # Serialize User info
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


