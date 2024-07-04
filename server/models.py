from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    # relationships
    restaurant_pizzas = relationship('RestaurantPizza', back_populates='restaurant')
    pizzas = relationship('Pizza', secondary='restaurant_pizzas', back_populates='restaurants')

    serialize_rules = ('-restaurant_pizzas.restaurant', '-pizzas.restaurants')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
        }

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    # relationships
    restaurant_pizzas = relationship('RestaurantPizza', back_populates='pizza')
    restaurants = relationship('Restaurant', secondary='restaurant_pizzas', back_populates='pizzas')

    serialize_rules = ('-restaurant_pizzas.pizza', '-restaurants.pizzas')

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, ForeignKey('restaurants.id'), nullable=False)
    pizza_id = db.Column(db.Integer, ForeignKey('pizzas.id'), nullable=False)

    # relationships
    restaurant = relationship('Restaurant', back_populates='restaurant_pizzas')
    pizza = relationship('Pizza', back_populates='restaurant_pizzas')

    serialize_rules = ('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas')

    @validates('price')
    def validate_price(self, key, value):
        if value < 0:
            raise ValueError("Price must be a positive integer")
        return value

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
