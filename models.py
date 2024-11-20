from sqlalchemy_serializer import SerializerMixin
from extensions import db, bcrypt
from sqlalchemy.orm import relationship
from sqlalchemy import CheckConstraint
from datetime import datetime
import re  # For email validation
from flask_login import UserMixin

class User(db.Model, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='customer') 

    # exclude password hash from serialization
    serialize_only = ('id', 'name', 'email', 'role')

    # Relationships
    cart = db.relationship('Cart', back_populates='user', uselist=False, cascade='all, delete-orphan')
    orders = db.relationship('Orders', back_populates='user', cascade='all, delete-orphan')
    payments = db.relationship('Payments', back_populates='user', cascade='all, delete-orphan')

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

    # Foreign Key
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))

    serialize_only = ('id', 'name', 'price', 'available_quantity', 'description', 'category', 'breed', 'age', 'image_url')

    # Relationship
    vendor = db.relationship('Vendor', back_populates='animals')
    cart_items = db.relationship('CartItem', back_populates='animal', cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', back_populates='animal', cascade='all, delete-orphan')

    def __repr__(self):
        return (f"<Animal(id={self.id}, name='{self.name}', category='{self.category}', breed='{self.breed}', age='{self.age}', price='{self.price}', image_url='{self.image_url}', vendor_id='{self.vendor_id}')>")
class Orders(db.Model, SerializerMixin):
    
    __tablename__ = 'orders'
    serialize_only = ('id', 'status', 'total_price', 'created_at', 'updated_at')
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    status = db.Column(db.String, default='Pending', nullable=False)
    total_price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    user = db.relationship('User', back_populates='orders')
    order_items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    payment = db.relationship('Payments', back_populates='order', uselist=False)
    
    __table_args__ = (
        CheckConstraint("status IN ('Pending', 'Completed', 'Failed')", name='check_order_status'),
    )
    
    def calculate_total_price(self):
        return sum(item.quantity * item.unit_price for item in self.order_items)
    
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

    # Relationships
    order = db.relationship('Orders', back_populates='order_items')
    animal = db.relationship('Animal', back_populates='order_items')
    
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

    # Relationships
    user = db.relationship('User', back_populates='payments')
    order = db.relationship('Orders', back_populates='payment')
    
    __table_args__ = (
        CheckConstraint("status IN ('Pending', 'Paid', 'Failed')", name='check_payment_status'),
    )
    
    def __repr__(self):
        return f"Payments('{self.id}', '{self.amount}', '{self.status}', '{self.payment_date}')"

class Vendor(db.Model, UserMixin, SerializerMixin):
    __tablename__ = 'vendors'

    # Primary Key: Unique identifier for each vendor
    id = db.Column(db.Integer, primary_key=True)

    # Basic vendor attributes
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    farm_name = db.Column(db.String(100), nullable=True)

    # Relationships
    animals = db.relationship('Animal', back_populates='vendor', cascade='all, delete-orphan')

    def set_password(self, password):

        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):

        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return (f"<Vendor(id={self.id}, name='{self.name}', email='{self.email}', "
                f"phone_number='{self.phone_number}', farm_name='{self.farm_name}')>")


# def set_password(self, password):
#     self.password = bcrypt.generate_password_hash(password).decode('utf-8')

# def check_password(self, password):
#     return bcrypt.check_password_hash(self.password, password)

class Cart(db.Model):
    __tablename__ = 'carts'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Key linking to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Cart creation date

    # Relationships
    cart_items = db.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')
    user = db.relationship('User', back_populates='cart')

    def __repr__(self):
        return f"<Cart user_id={self.user_id} created_at={self.created_at}>"

    def to_dict(self, include_user=False):
        """
        Serialize Cart to dictionary. Optionally include User info without including `user.cart`
        to avoid recursion.
        """
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'cart_items': [item.to_dict() for item in self.cart_items]  # Serialize CartItems without circular reference
        }
        if include_user:
            data['user'] = {
                'id': self.user.id,
                'name': self.user.name  # Add other relevant fields here, excluding `cart` relationship to avoid recursion
            }
        return data

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
        return f"<CartItem cart_id={self.cart_id} animal_id={self.animal_id} quantity={self.quantity}>"

    def to_dict(self, include_animal=False):
        """
        Serialize CartItem to dictionary, optionally including related Animal details to avoid circular references.
        """
        data = {
            'id': self.id,
            'cart_id': self.cart_id,
            'animal_id': self.animal_id,
            'quantity': self.quantity,
            'added_at': self.added_at.isoformat()
        }
        if include_animal:
            data['animal'] = {
                'id': self.animal.id,
                'name': self.animal.name,  # Add other relevant fields here, excluding `cart_items` to avoid recursion
            }
        return data

