from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt

class Orders(db.Model, SerializerMixin):
    
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
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
    # animal_id = db.Column(db.Integer, db.ForeignKey('animals.id', ondelete='CASCADE'))
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Float)
    subtotal = db.Column(db.Float)
    
    def __repr__(self):
        return f"OrderItem('{self.id}', '{self.quantity}', '{self.price}')"

class Payments(db.Model, SerializerMixin):
    
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'))
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    amount = db.Column(db.Float)
    status = db.Column(db.String)
    payment_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def __repr__(self):
        return f"Payments('{self.id}', '{self.amount}', '{self.status}', '{self.payment_date}')"