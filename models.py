from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import func, extract


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1092@localhost:5432/alpha_product'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default= datetime.utcnow)

    sales = db.relationship("Sale", backref = 'product')
 

class Sale(db.Model):
    __tablename__ = 'sale'
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    customer_id =  db.Column(db.Integer, db.ForeignKey('customer.id'), nullable  =False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)
    sale_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    customer = db.relationship('Customer', back_populates = 'sale')

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(100), nullable = False)
    last_name = db.Column(db.String(100), nullable = False)
    age = db.Column(db.Integer, nullable = False)
    email = db.Column(db.String(100), nullable = False)

    sale = db.relationship('Sale', back_populates = 'customer')






 
