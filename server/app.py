#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize database and migration
migrate = Migrate(app, db)
db.init_app(app)

# Index route
@app.route('/')
def index():
    return '<h1>Code Challenge</h1>'

# Route for fetching and creating Heroes
@app.route('/heroes', methods=['GET', 'POST'])
def heroes():
    if request.method == 'GET':
        heroes = Hero.query.all()
        return jsonify([hero.to_dict() for hero in heroes]), 200
    
    if request.method == 'POST':
        data = request.get_json()
        new_hero = Hero(name=data['name'], super_name=data['super_name'])
        db.session.add(new_hero)
        db.session.commit()
        return jsonify(new_hero.to_dict()), 201

@app.route('/heroes/<int:id>', methods=['GET'])
def hero_detail(id):
    hero = Hero.query.get(id)
    if not hero:
        return jsonify({'error': 'Hero not found'}), 404
    return jsonify(hero.to_dict()), 200
    


# Route for fetching and creating Powers
@app.route('/powers', methods=['GET', 'POST'])
def powers():
    if request.method == 'GET':
        powers = Power.query.all()
        return jsonify([power.to_dict() for power in powers]), 200

    if request.method == 'POST':
        data = request.get_json()
        new_power = Power(name=data['name'], description=data['description'])
        db.session.add(new_power)
        db.session.commit()
        return jsonify(new_power.to_dict()), 201
    
@app.route('/powers/<int:id>', methods=['GET', 'PATCH'])
def power_detail(id):
    power = Power.query.get(id)
    
    if not power:
        return jsonify({'error': 'Power not found'}), 404

    if request.method == 'GET':
        return jsonify(power.to_dict()), 200
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    
    if not power:
        return jsonify({'error': 'Power not found'}), 404

    data = request.get_json()

    if 'description' in data:
        description = data['description']
        if not isinstance(description, str) or len(description) < 20:
            return jsonify({'error': 'Description must be at least 20 characters long'}), 400
        power.description = description

    db.session.commit()
    return jsonify(power.to_dict()), 200


# Route for fetching and creating HeroPower relationships
@app.route('/hero_powers', methods=['GET', 'POST'])
def hero_powers():
    if request.method == 'GET':
        hero_powers = HeroPower.query.all()
        return jsonify([hero_power.to_dict() for hero_power in hero_powers]), 200

    if request.method == 'POST':
        data = request.get_json()
        new_hero_power = HeroPower(
            strength=data['strength'],
            hero_id=data['hero_id'],
            power_id=data['power_id']
        )
        db.session.add(new_hero_power)
        db.session.commit()
        return jsonify(new_hero_power.to_dict()), 201
    
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    
    # Validate strength
    strength = data.get('strength')
    if strength not in ['Strong', 'Weak', 'Average']:
        return jsonify({'error': 'Strength must be one of: Strong, Weak, Average'}), 400

    new_hero_power = HeroPower(
        strength=strength,
        hero_id=data['hero_id'],
        power_id=data['power_id']
    )
    
    db.session.add(new_hero_power)
    db.session.commit()
    return jsonify(new_hero_power.to_dict()), 201


if __name__ == '__main__':
    app.run(port=5555, debug=True)
