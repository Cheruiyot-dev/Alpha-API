import sentry_sdk
from flask import request
from sentry_sdk import capture_exception
from models import Product, Sale, Customer, app, db
from flask import jsonify
import requests
from datetime import datetime
from datetime import date as dt
from sqlalchemy import func, extract
from sqlalchemy import join

sentry_sdk.init(
    dsn="https://cd49088963241378968fb298425dd04a@o4506695434698752.ingest.sentry.io/4506701235945472",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)


@app.route("/products", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def prods():
    if request.method == "GET":
        try:
            prods = Product.query.all()
            res = []
            for i in prods:
                res.append({"id": i.id, "name": i.name, "price": i.price, "created_at" : i.created_at})

            return jsonify(res), 200
        except Exception as e:
            capture_exception(e)
            return jsonify("error:", str(e))
    elif request.method == "POST":
        if request.is_json:
            try:
                data = request.json
                print(type(data))
                new_data = Product( id=data['id'], name=data['name'], price=data['price'], created_at =data['created_at'])
                db.session.add(new_data)
                db.session.commit()
                r = "Successfully stored product id: " + str(new_data.id)
                res = {"Result": r}
                return jsonify(res), 201
            except Exception as e:
                print(e)
                return jsonify({"Error": str(e)}), 500

        else:
            return jsonify({"Error": "data is not json"}), 400
    else:
        return jsonify({"Error": "Method is not allowed."}), 403


@app.route("/product/<int:product_id>", methods=["GET"])
def get_single_product(product_id):
    single_product = Product.query.get(product_id)
    if single_product:
        s_product = {
            "id": single_product.id,
            "name": single_product.name,
            "price": single_product.price
        }

        return jsonify(s_product), 200

    else:
        return jsonify({"error": "Product not found"}), 404


@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.json
    # print(type(data))
    new_name = data.get("name")
    new_price = data.get("price")

    product = Product.query.get(product_id)
    # print(type(product))
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    if new_name:
        product.name = new_name
    if new_price:
        product.price = new_price

    db.session.commit()

    return jsonify({'message': 'Product updated successfully'}), 200


@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify("error:", "Product not found"), 404
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify("Success:" f"Product {product_id} deleted successfully"), 200

    except Exception as e:
        db.session.rollback()
        return jsonify("error", str(e))

# sale routes


@app.route('/sales', methods=['GET', 'POST'])
def sales():
    if request.method == 'GET':
        try:
            sales = Sale.query.all()
            s_dict = []
            for sale in sales:
                s_dict.append({"id": sale.id, "pid": sale.pid,
                              "quantity": sale.quantity, "created_at": sale.created_at, "sale_date": sale.sale_date})
            return jsonify(s_dict)
        except Exception as e:
            print(e)
            # capture_exception(e)
            return jsonify({})
    elif request.method == 'POST':
        if request.is_json:
            try:
                data = request.json
                new_sale = Sale(pid=data.get(
                    'pid'), quantity=data.get('quantity'))
                db.session.add(new_sale)
                db.session.commit()
                s = "sales added successfully." + str(new_sale.id)
                sel = {"result": s}
                return jsonify(sel), 201
            except Exception as e:
                print(e)
                # capture_exception(e)
                return jsonify({"error": "Internal Server Error"}), 500
        else:
            return jsonify({"error": "Data is not JSON."}), 400
    else:
        return jsonify({"error": "Method not allowed."}), 400

@app.route("/sales/<sale_id>", methods=["GET"])
def get_single_sale(sale_id):
    try:
        sale = Sale.query.get(sale_id)
        print(type(sale))

        if sale is None:
            return jsonify("Sale not found"), 404
        else:
            sale = {
                "id": sale.id,
                "pid": sale.pid,
                "customer_id": sale.customer_id,
                "quantity": sale.quantity,
                "created_at": sale.created_at
            }

            return jsonify(sale), 200

    except Exception as e:
        return jsonify("error:", str(e)), 500


@app.route("/sales/stats/", methods=["GET"])
def top_selling_product():
     try:
        top_product = db.session.query(Sale.pid, Product.name, db.func.sum(Sale.quantity).label('total_sold')) \
        .join(Product, Sale.pid == Product.id) \
        .group_by(Sale.pid, Product.name) \
        .order_by(db.desc('total_sold')) \
        .all() 
        #  .limit(10)     
        top_product_list = []
        #  print(type(top_product))
        for i in top_product:
            #  print(type(i))
            top_p = {
                "product_id" : i.pid,
                "product_name" : i.name,
                "total_sold" : i.total_sold
            }
            top_product_list.append(top_p)
     except Exception as e:
         return jsonify("Error:", str(e)), 400 
     return jsonify(top_product_list), 200





    
    





#  Customer routes

@app.route("/customers", methods=["GET", "POST"])
def get_all_customers():
    if request.method == "GET":
        try:
            customers = Customer.query.all()   
            # print(type(customers))
            customer_list = []

            for customer in customers:
                customer_list.append({"id": customer.id, "age": customer.age, "email": customer.email, "first_name": customer.first_name, "last_name": customer.last_name})
                # print(type(customer))
            return jsonify(customer_list), 200

        except Exception as e:
            return jsonify("error:", str(e))
    elif request.method == "POST":
        if request.is_json:
            try:
                data = request.json
                new_customer = Customer(id=data.get("id"),age=data.get("age"), email=data.get("email"), first_name=data.get(
                    "first_name"), last_name=data.get(
                    "last_name"))
                db.session.add(new_customer)
                db.session.commit()

                return jsonify("New customer added successfully"), 201
            except Exception as e:
                return jsonify("error", str(e)), 400
        else:
            return jsonify({"Error": "data is not json"}), 400
    else:
        return jsonify({"Error": "Method is not allowed."}), 403


@app.route("/customers/<customer_id>", methods=["GET"])
def get_single_customer(customer_id):
    try:
        single_customer = Customer.query.get(customer_id)
        if single_customer is None:
            return jsonify({"error:": "Customer not found"}), 404

        else:
            customer_data = {"id": single_customer.id, "age": single_customer.age, "email": single_customer.email, "first_name": single_customer.first_name, "last_name": single_customer.last_name}
            return jsonify(customer_data), 200
    except Exception as e:
        return jsonify("error:", str(e)), 400


#  alphavantage - dashboard route
@app.route("/dashboard", methods=["GET"])
def dashboard():
    # api_key = "2Z5BUFU7HVV3C5ZS"
    # url = "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=KES&apikey=" + api_key

    # r = requests.get(url)
    # print("Response is .....", r.json())
    # data = r.json()
    # # new = data.append(r)
    # print(type(data))
    # r = requests.get(url)
    # print("Response is .....", r.json())
    # data = r.json()
    # # new = data.append(r)
    # print(type(data))

    # exchange_rate = float(
    #     data['Realtime Currency Exchange Rate']['5. Exchange Rate'])
    # new_data = {'KSH': exchange_rate}

    # print(new_data)

    # return new_data

# Display the currency in my web app.
# Consume any other public APIs.
# Display the currency in web app.

    sales_per_product = db.session.query(Product.name,
                                         func.sum(Sale.quantity * Product.price). label('sales_product')
                                         ).join(
                                             Product, Sale.pid == Product.id 
                                             ).group_by(Product.name).limit(10)
    salesproduct_data = [{'name' : name, 'sales_product': sales_product} for name, sales_product in sales_per_product]

    return jsonify(salesproduct_data),200
    


    
@app.route("/sales_trend/<interval>", methods=["GET"])
def get_sales_trend(interval):
    sales_trend_data = None

    if interval == 'day':
        sales_trend_data = db.session.query(
            func.date_trunc('day', Sale.sale_date).label('date'),
            func.sum(Sale.quantity).label('total_quantity_sold'),
            func.sum(Sale.quantity * Product.price).label('total_sales_amount')
        ).join(
            Product, Sale.pid == Product.id
        ).group_by(
            func.date_trunc('day', Sale.sale_date)
        ).order_by(
            func.date_trunc('day', Sale.sale_date)
        ).all()
    elif interval == 'week':
        sales_trend_data = db.session.query(
            func.date_trunc('week', Sale.sale_date).label('date'),
            func.sum(Sale.quantity).label('total_quantity_sold'),
            func.sum(Sale.quantity * Product.price).label('total_sales_amount')
        ).join(
            Product, Sale.pid == Product.id
        ).group_by(
            func.date_trunc('week', Sale.sale_date)
        ).order_by(
            func.date_trunc('week', Sale.sale_date)
        ).all()
    elif interval == 'month':
        sales_trend_data = db.session.query(
            func.date_trunc('month', Sale.sale_date).label('date'),
            func.sum(Sale.quantity).label('total_quantity_sold'),
            func.sum(Sale.quantity * Product.price).label('total_sales_amount')
        ).join(
            Product, Sale.pid == Product.id
        ).group_by(
            func.date_trunc('month', Sale.sale_date)
        ).order_by(
            func.date_trunc('month', Sale.sale_date)
        ).all()
    elif interval == 'quarter':
        sales_trend_data = db.session.query(
            func.date_trunc('quarter', Sale.sale_date).label('date'),
            func.sum(Sale.quantity).label('total_quantity_sold'),
            func.sum(Sale.quantity * Product.price).label('total_sales_amount')
        ).join(
            Product, Sale.pid == Product.id
        ).group_by(
            func.date_trunc('quarter', Sale.sale_date)
        ).order_by(
            func.date_trunc('quarter', Sale.sale_date)
        ).all()
    elif interval == 'year':
        sales_trend_data = db.session.query(
            func.date_trunc('year', Sale.sale_date).label('date'),
            func.sum(Sale.quantity).label('total_quantity_sold'),
            func.sum(Sale.quantity * Product.price).label('total_sales_amount')
        ).join(
            Product , Sale.pid == Product.id
        ).group_by(
            func.date_trunc('year', Sale.sale_date)
        ).order_by(
            func.date_trunc('year', Sale.sale_date)
        ).all()

    # Process the sales trend data and return as JSON
    if sales_trend_data is not None:
        trend_data_list = []
        for trend_item in sales_trend_data:
            print(type(trend_item))
            trend_data_list.append({
                "date": trend_item[0].strftime("%Y-%m-%d"),
                "total_quantity_sold": trend_item[1],
                "total_sales_amount" : trend_item[2]
            })
        # return jsonify(trend_data_list), 200
    # sales per product

   
    return jsonify({'trend_data_list': trend_data_list}), 200


    # else:
    #     return jsonify({"error": "No data available for the specified interval"}), 404


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # db.drop_all()
        app.run(debug=True)
