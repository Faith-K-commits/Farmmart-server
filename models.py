from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt
from sqlalchemy.orm import relationship
from sqlalchemy import CheckConstraint
from datetime import datetime
import re  # For email validation

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='customer') 

    # exclude password hash from serialization
    serialize_rules = ('-password_hash',)

    # Check constraint to ensure only specific roles are allowed
    __table_args__ = (
        CheckConstraint(role.in_(['admin', 'customer']), name='check_valid_role'),
    )

    def set_password(self, password):

        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):

        return bcrypt.check_password_hash(self.password_hash, password)

    def is_admin(self):
        #Checks if the user has an admin role
        return self.role == 'admin'

    @staticmethod
    def is_valid_email(email):
        #Validate the format of an email address using regular expression
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    def __repr__(self):
        return f'<User {self.name}, Role {self.role}>'

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

    # Foreign Key linking to the Vendor (farmer) who listed the animal
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=True) #Temporary Null value for testing (Remember to change this when vendor model is ready)

    # Relationship to Vendor model; allows access to the vendor's information from an animal instance
    vendor = db.relationship('Vendor', back_populates='animals')

    # Relationship to CartItem model; allows access to all cart items that include this animal
    # Useful for tracking demand and inventory across user carts
    cart_items = db.relationship('CartItem', back_populates='animal', lazy=True)

    def __repr__(self):
        return (f"<Animal(id={self.id}, name='{self.name}', category='{self.category}', breed='{self.breed}', age='{self.age}', price='{self.price}', image_url='{self.image_url}', vendor_id='{self.vendor_id}')>")
class Orders(db.Model, SerializerMixin):
    
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    status = db.Column(db.String, default='Pending')
    total_price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def __repr__(self):
        return f"Order('{self.id}', '{self.status}', '{self.total_price}')"

class OrderItem(db.Model, SerializerMixin):
    
    __tablename__ = 'order_item'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'))
    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id', ondelete='CASCADE'))
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Float)
    subtotal = db.Column(db.Float)
    
    def __repr__(self):
        return f"OrderItem('{self.id}', '{self.quantity}', '{self.price}')"

class Payments(db.Model, SerializerMixin):
    
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    amount = db.Column(db.Float)
    status = db.Column(db.String)
    payment_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def __repr__(self):
        return f"Payments('{self.id}', '{self.amount}', '{self.status}', '{self.payment_date}')"

class Vendor(db.Model, SerializerMixin):
    __tablename__ = 'vendors'

    # Primary Key: Unique identifier for each vendor
    id = db.Column(db.Integer, primary_key=True)

    # Basic vendor attributes
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    farm_name = db.Column(db.String(100), nullable=True)

    # Relationship to Animal model; allows access to all animals listed by this vendor
    animals = db.relationship('Animal', back_populates='vendor', cascade='all, delete-orphan')

    def __repr__(self):
        return (f"<Vendor(id={self.id}, name='{self.name}', email='{self.email}', "
                f"phone_number='{self.phone_number}', farm_name='{self.farm_name}')>")


def set_password(self, password):
    self.password = bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(self, password):
    return bcrypt.check_password_hash(self.password, password)

class Cart(db.Model):
    __tablename__ = 'carts'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Key linking to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Cart creation date
    cart_items = db.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')

    # User relationship
    user = db.relationship('User', back_populates='cart')
    #user = db.relationship('User', back_populates='cart')

    def __repr__(self):
        return f"<Cart user_id={self.user_id} created_at={self.created_at}>"
    def __repr__(self):
        return f"<Cart user_id={self.user_id} created_at={self.created_at}>"

    def to_dict(self):
        # Serialize Cart to dictionary, including the CartItems and User info
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'cart_items': [item.to_dict() for item in self.cart_items],  # Serialize CartItems
            'user': self.user.to_dict(),  # Serialize User info
            'user': self.user.to_dict(),  # Serialize User info
            'animal': self.animal.to_dict()  # Serialize the associated animal details
        }