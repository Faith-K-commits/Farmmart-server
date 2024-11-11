from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt
from sqlalchemy.orm import relationship

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
    # cart_items = db.relationship('CartItem', backref='animal', lazy=True)

    def __repr__(self):
        return (f"<Animal(id={self.id}, name='{self.name}', category='{self.category}', breed='{self.breed}', age='{self.age}', price='{self.price}', image_url='{self.image_url}', vendor_id='{self.vendor_id}')>")
    


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
    # animals = db.relationship('Animal', back_populates='vendor', cascade='all, delete-orphan')

    def __repr__(self):
        return (f"<Vendor(id={self.id}, name='{self.name}', email='{self.email}', "
                f"phone_number='{self.phone_number}', farm_name='{self.farm_name}')>")


def set_password(self, password):
    self.password = bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(self, password):
    return bcrypt.check_password_hash(self.password, password)





        