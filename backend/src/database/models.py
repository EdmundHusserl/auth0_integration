import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
import json


db = SQLAlchemy()


def setup_db(app):
    """
        binds a flask application and a SQLAlchemy service
    """
    db.app = app
    db.init_app(app)


def db_drop_and_create_all():
    """
        drops the database tables and starts fresh
        can be used to initialize a clean database
    """
    db.drop_all()
    db.create_all()


class Drink(db.Model):
    """
        Drink
        a persistent drink entity, extends the base SQLAlchemy Model
    """
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    title = Column(String(80), unique=True)
    # the ingredients blob - this stores a lazy json blob
    # the required datatype is [{'color': string, 'name':string, 'parts':number}]
    recipe =  Column(String(180), nullable=False)

    def short(self):
        """
            Short form representation of the Drink model.
        """
        print(json.loads(self.recipe))
        short_recipe = [{'color': r['color'], 'parts': r['parts']} for r in json.loads(self.recipe)]
        return {
            'id': self.id,
            'title': self.title,
            'recipe': short_recipe
        }

    def long(self):
        """
            Long form representation of the Drink model.
        """
        return {
            'id': self.id,
            'title': self.title,
            'recipe': json.loads(self.recipe)
        }

    def insert(self):
        """
            Inserts a new model into a database.
            The model must have a unique name.
            The model must have a unique id or null id.
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
            Deletes a new model into a database the model must exist in the database
        """
        db.session.delete(self)
        db.session.commit()

    def update(self):
        """
            Updates a new model into a database the model must exist in the database
        """
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.short())
