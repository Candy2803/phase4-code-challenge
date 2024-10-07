#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os
from flask_cors import CORS

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
CORS(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


@app.route("/heroes")
def heroes():
    heroes = Hero.query.all()
    response = [hero.to_dict(only=("id", "name", "super_name")) for hero in heroes]
    return make_response(response, 200)


@app.route("/heroes/<int:id>")
def hero(id):
    hero = Hero.query.filter_by(id=id).first()
    if hero:
        response = hero.to_dict()
        return make_response(response, 200)
    else:
        return make_response({"error": "Hero not found"}, 404)


@app.route("/powers")
def powers():
    powers = Power.query.all()
    response = [power.to_dict(only=("description", "id", "name")) for power in powers]
    return make_response(response, 200)


@app.route("/powers/<int:id>", methods=["GET", "PATCH"])
def power(id):
    power = Power.query.filter_by(id=id).first()
    if request.method == "GET":
        if power:
            response = power.to_dict(only=("description", "id", "name"))
            return make_response(response, 200)
        else:
            return make_response({"error": "Power not found"}, 404)
    elif request.method == "PATCH":
        if not power:
            return make_response({"error": "Power not found"}, 404)
        data = request.get_json() if request.is_json else request.form
        try:
            for key, value in data.items():
                setattr(power, key, value)
            db.session.commit()
            return make_response(power.to_dict(), 200)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


@app.route("/hero_powers", methods=["POST"])
def hero_powers():
    try:
        data = request.get_json() if request.is_json else request.form
        hero_power = HeroPower(**data)
        db.session.add(hero_power)
        db.session.commit()
        return make_response(hero_power.to_dict(), 200)
    except ValueError:
        return make_response({"errors": ["validation errors"]}, 400)


if __name__ == "__main__":
    app.run(port=5555, debug=True)