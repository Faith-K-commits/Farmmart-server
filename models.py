from sqlalchemy_serializer import SerializerMixin
from config import db, bycrypt
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

# Vendor (Farmer) model: represents vendors who list animals for sale.
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

# Encrypt the password before storing it in the database
    def set_password(self, raw_password):
        self.password = bycrypt.generate_password_hash(raw_password).decode('utf-8')

    # Verify password
    def check_password(self, raw_password):
        return bycrypt.check_password_hash(self.password, raw_password)
