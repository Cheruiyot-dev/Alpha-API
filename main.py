import sentry_sdk
from flask import request
from sentry_sdk import capture_exception
from models import Product, Sales, Customer, app, db
from flask import jsonify


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
                res.append({"id": i.id, "name": i.name, "price": i.price})

            return jsonify(res), 200
        except Exception as e:
            capture_exception(e)
            return "error in app"
    elif request.method == "POST":
        if request.is_json:
            try:
                data = request.json
                print(type(data))
                new_data = Product(name=data['name'], price=data['price'])
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
        return jsonify("Success:" "Product deleted successfully"), 200

    except Exception as e:
        db.session.rollback()
        return jsonify("error", str(e))



@app.route('/sales', methods=['GET', 'POST'])
def sales():
    if request.method == 'GET':
        try:
            sales = Sales.query.all()
            s_dict = []
            for sale in sales:
                s_dict.append({"id": sale.id, "pid": sale.pid,
                              "quantity": sale.quantity, "created_at": sale.created_at, "sale_date" : sale.sale_date})
            return jsonify(s_dict)
        except Exception as e:
            print(e)
            # capture_exception(e)
            return jsonify({})
    elif request.method == 'POST':
        if request.is_json:
            try:
                data = request.json
                new_sale = Sales(pid=data.get(
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


@app.route("/sales/<sale_id>", methods = ["GET"])
def get_single_sale(sale_id):
    try:
        sale = Sales.query.get(sale_id)
        print(type(sale))

        if  sale is None:
            return jsonify("Sale not found"), 404
        else:
            sale = {
                "id" : sale.id,
                "pid" : sale.pid,
                "quantity" : sale.quantity,
                "created_at" : sale.created_at
            }

            return jsonify(sale), 200

    except Exception as e:
        return jsonify("error:", str(e)), 500
    
# Customer routes


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)
