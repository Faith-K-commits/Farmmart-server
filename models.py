from sqlalchemy_serializer import SerializerMixin
from config import db, bycrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
import re  # For email validation


#============================================================================
#User Model
#============================================================================

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
        
        self.password_hash = bycrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        
        return bycrypt.check_password_hash(self.password_hash, password)

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
