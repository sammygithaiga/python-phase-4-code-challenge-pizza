#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods= ['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    restaurant_data = [restaurant.to_dict() for restaurant in restaurants]
    return jsonify(restaurant_data), 200

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return {"error": "Restaurant not found"}, 404

    
    print(f"Restaurant ID: {restaurant.id}, Name: {restaurant.name}, Address: {restaurant.address}")

    try:
        pizzas = [{
            "id": rp.pizza.id,
            "name": rp.pizza.name,
            "ingredients": rp.pizza.ingredients,
            "price": rp.price
        } for rp in restaurant.restaurant_pizzas]

        
        print(f"Pizzas: {pizzas}")

        return {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "pizzas": pizzas
        }, 200
    except Exception as e:
        
        print(f"Error: {e}")
        return {"error": str(e)}, 500

    
@app.route('/restaurants/<int:id>', methods= ['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return make_response('', 204)
    else:
        return jsonify({"error": "Restaurant not found"}), 404
    
@app.route('/pizzas', methods= ['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizza_data = [pizza.to_dict() for pizza in pizzas]
    return jsonify(pizza_data), 200

@app.route('/restaurants_pizzas', methods= ['POST'])
def create_restaurant_pizza():
    data = request.get_json()

    try: 
        price = data['price']
        pizza_id = data['pizza_id']
        restaurant_id= data['restaurant_id']

        if not all([price, pizza_id, restaurant_id]):
            raise ValueError("Missing required fields")

        new_restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        return jsonify(new_restaurant_pizza.to_dict()), 201
    except KeyError as e:
        return jsonify({"error", f"Missing key in JSON: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400

if __name__ == "__main__":
    app.run(port=5555, debug=True)

