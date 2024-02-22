from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1092@localhost:5432/alpha_product'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default= datetime.utcnow)

    sales = db.relationship("Sales", backref = 'product')
    orders = db.relationship('Order', back_populates = 'product')

class Sales(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    customer_id =  db.Column(db.Integer, db.ForeignKey('customer.id'), nullable  =False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)
    sale_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    customer = db.relationship('Customer', back_populates = 'sales')

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    age = db.Column(db.Integer, nullable = False)
    email = db.Column(db.String(100), nullable = False)

    sales = db.relationship('Sales', back_populates = 'customer')
    orders = db.relationship('Order', back_populates = 'customer')


class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    customer = db.relationship("Customer", back_populates="orders")
    product = db.relationship("Product", back_populates="orders")

class Report(db.Model):
    __tablename__ = 'report'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    content = db.Column(db.String)
    generated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

 
