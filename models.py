import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

database_path = "postgres://ztneoadoikftem:3fd4a6b14b191415917638c49f66f561e44e202f4ee10b76780d4790ea548552@ec2-34-230-198-12.compute-1.amazonaws.com:5432/d3m0t7alhu7ut1"
if database_path.startswith("postgres://"):
  database_path = database_path.replace("postgres://", "postgresql://", 1)

db = SQLAlchemy()

def setup_db(app, database_path): 
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

  
class Tree(db.Model): 
  __tablename__ = "trees"

  id = Column(Integer, primary_key=True)
  name = Column(String)
  farmer_id = Column(Integer, db.ForeignKey('farmers.id'))
  forest_id = Column(Integer, db.ForeignKey('forests.id'))

  def insert(self): 
    db.session.add(self)
    db.session.commit()
  
  def update(self): 
    db.session.commit()

  def delete(self): 
    db.session.delete(self)
    db.session.commit()
  
  def format(self):
    return {
      'id': self.id,
      'name': self.name,
      'farmer_id': self.farmer_id,
      'forest_id': self.forest_id
      }
  


class Forest(db.Model): 
  __tablename__ = "forests"

  id = Column(Integer, primary_key=True)
  name = Column(String)
  location = Column(String)

  trees = db.relationship('Tree', backref=db.backref('forests'), lazy=True, cascade='delete')

  def insert(self): 
    db.session.add(self)
    db.session.commit()
  
  def update(self): 
    db.session.commit()

  def delete(self): 
    db.session.delete(self)
    db.session.commit()
  
  def format(self):
    return {
      'id': self.id,
      'name': self.name,
      'location': self.location,
    }

  def get_trees(self): 
    return [tree.format() for tree in self.trees]
    


class Farmer(db.Model): 
  __tablename__ = "farmers"

  id = Column(Integer, primary_key=True)
  name = Column(String)

  trees = db.relationship('Tree', backref=db.backref('farmers'), lazy=True)

  def insert(self): 
    db.session.add(self)
    db.session.commit()
  
  def update(self): 
    db.session.commit()

  def delete(self): 
    db.session.delete(self)
    db.session.commit()
  
  def format(self):
    return {
      'id': self.id,
      'name': self.name,
    }

  def get_trees(self): 
    return [tree.format() for tree in self.trees]
    