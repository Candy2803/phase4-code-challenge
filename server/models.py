from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, CheckConstraint, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

# Hero Model
class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    super_name = db.Column(db.String, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'super_name': self.super_name
        }

    # Many-to-many relationship through HeroPower
    powers = relationship('HeroPower', back_populates='hero', cascade="all, delete")

    # Serialization rules to avoid deep recursion
    serialize_rules = ('-powers.hero',)

    def __repr__(self):
        return f'<Hero {self.id} {self.name} ({self.super_name})>'

# Power Model
class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    # Many-to-many relationship through HeroPower
    heroes = relationship('HeroPower', back_populates='power', cascade="all, delete")

    # Serialization rules to avoid deep recursion
    serialize_rules = ('-heroes.power',)
    
    @validates('description')
    def validate_description(self, key, value):
        if len(value) < 20:
            raise ValueError("Description must be at least 20 characters long")
        return value

    def __repr__(self):
        return f'<Power {self.id} {self.name}>'

# HeroPower Model (Join table)
class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)
    hero_id = db.Column(db.Integer, ForeignKey('heroes.id', ondelete='CASCADE'), nullable=False)
    power_id = db.Column(db.Integer, ForeignKey('powers.id', ondelete='CASCADE'), nullable=False)

    # Relationships to Hero and Power
    hero = relationship('Hero', back_populates='powers')
    power = relationship('Power', back_populates='heroes')

    # Validation for strength attribute
    @validates('strength')
    def validate_strength(self, key, value):
        if value not in ['Weak', 'Average', 'Strong']:
            raise ValueError("Strength must be 'Weak', 'Average', or 'Strong'")
        return value

    # Serialization rules to limit recursion
    serialize_rules = ('-hero.powers', '-power.heroes')

    def __repr__(self):
        return f'<HeroPower {self.id} Strength: {self.strength}>'
