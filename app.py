import os
from flask import Flask, request, abort, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, distinct
from flask_cors import CORS
import json
from auth import requires_auth, AuthError
from models import setup_db, database_path, Tree, Farmer, Forest, db

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  CORS(app)
  setup_db(app, database_path)

  # HOMEPAGE
  @app.route('/', methods=['GET'])
  def home():
      return jsonify({'message': 'Hello,hello, World!'})
    
  
  # GET TREES
  @app.route('/trees', methods=['GET'])
  def get_trees(): 
    trees = [tree.format() for tree in Tree.query.all()]
    return jsonify({
      'success': True,
      'trees': trees,
      "number_of_trees": len(trees)
    })

  # GET FORESTS
  @app.route('/forests', methods=['GET'])
  def get_forests(): 
    forests = [forest.format() for forest in Forest.query.all()]
    return jsonify({
      'success': True,
      'forests': forests
    })

  # GET FARMERS
  @app.route('/farmers', methods=['GET'])
  def get_farmers(): 
    farmers = [farmer.format() for farmer in Farmer.query.all()]
    return jsonify({
      'success': True,
      'farmers': farmers
    })

  # GET ONE FARMER
  @app.route('/farmers/<int:id>', methods=['GET'])
  def get_farmer_id(id): 
    farmer = Farmer.query.filter(Farmer.id == id).one_or_none()
    if farmer is None: 
      abort(404)

    # Getting tree count by type for selected farmer
    farmer_trees_by_type_query = db.session.query(Tree.name, func.count(Tree.id).label('count')).filter(Tree.farmer_id == id).group_by(Tree.name) 
    tree_count_by_type = {row.name: row.count for row in farmer_trees_by_type_query}


    return jsonify({
      'success': True,
      'farmer': farmer.format(),
      'trees': tree_count_by_type,
      'number_of_trees': len(farmer.get_trees())
    })

  # GET ONE FOREST
  @app.route('/forests/<int:id>', methods=['GET'])
  def get_forest_id(id): 
    forest = Forest.query.filter(Forest.id == id).one_or_none()
    if forest is None: 
      abort(404)

    # Getting tree count by type for selected forest
    forest_trees_by_type_query = db.session.query(Tree.name, func.count(Tree.id).label('count')).filter(Tree.forest_id == id).group_by(Tree.name) 
    tree_count_by_type = {row.name: row.count for row in forest_trees_by_type_query}

    # Getting number of farmers for selected forest
    farmer_count_query = db.session.query(func.count(distinct(Tree.farmer_id))).filter(Tree.forest_id == id)
    # try/except block to get the count of unique farmers - better way to do this??
    try: 
      farmer_count = farmer_count_query[0][0]
    except: 
      farmer_count = 0

    return jsonify({
      'success': True,
      'forest': forest.format(),
      'trees': tree_count_by_type,
      'number_of_trees': len(forest.get_trees()),
      'farmer_count': farmer_count
    })

  #CREATE FARMER
  @app.route('/farmers', methods=['POST'])
  @requires_auth('post:farmer')
  def create_farmer(payload):
    try:
      body = request.get_json()
      name = body.get('name', None)

      farmer = Farmer(name=name) 

      farmer.insert()

      return jsonify({
        "success": True,
        "created": farmer.format(),
        "farmers": [farmer.format() for farmer in Farmer.query.all()]
      })
    
    except Exception as e: 
      print(e)
      abort(422)

  #EDIT FARMER
  @app.route('/farmers/<int:id>', methods=['PATCH'])
  @requires_auth('patch:farmer')
  def update_farmer(payload, id):
    try:
      body = request.get_json()
      name = body.get('name', None)

      farmer = Farmer.query.filter(Farmer.id == id).one_or_none()
       
      if farmer is None: 
         abort(404)

      farmer.name = name

      farmer.update()

      return jsonify({
        "success": True,
        "modified": farmer.format()
      })
    
    except Exception as e: 
      print(e)
      abort(422)

  # CREATE FOREST
  @app.route('/forests', methods=['POST'])
  @requires_auth('post:forest')
  def create_forest(payload):
    try:
      body = request.get_json()
      name = body.get('name', None)
      location = body.get('location', None)

      forest = Forest(name=name, location=location) 

      forest.insert()

      return jsonify({
        "success": True,
        "created": forest.format(),
        "forests": [forest.format() for forest in Forest.query.all()]
      })
    
    except Exception as e: 
      print(e)
      abort(422)

  #CREATE TREE
  @app.route('/trees', methods=['POST'])
  @requires_auth('post:tree')
  def create_tree(payload):
    try:
      body = request.get_json()
      name = body.get('name', None)
      farmer_id = body.get('farmer_id', None)
      forest_id = body.get('forest_id', None)
      quantity = body.get('quantity')

      # this is not working properly
      if Farmer.query.filter(id==farmer_id).one_or_none is None:
        print(f'Farmer with id {farmer_id} does not exist')
        abort(404)
        
      if Forest.query.filter(id==forest_id).one_or_none is None:
        print(f'Forest with id {forest_id} does not exist')
        abort(404)

      trees = []
      for i in range(quantity): 
        tree = Tree(name=name, farmer_id=farmer_id, forest_id=forest_id)
        trees.append(tree)

      for tree in trees: 
        tree.insert()

      return jsonify({
        "success": True,
        "created": [tree.format() for tree in trees],
        "total_trees": len([tree for tree in Tree.query.all()])
      })
    
    except Exception as e: 
      print(e)
      abort(422)

  
  #DELETE TREE
  @app.route('/trees/<int:id>', methods=['DELETE'])
  def delete_tree(id): 
    try: 
      tree = Tree.query.filter(Tree.id == id).one_or_none()
      if tree is None: 
        abort(404)
      tree.delete()

      return jsonify({
        "success": True, 
        "deleted": id,
        "total_trees": len(Tree.query.all())
      })

    except Exception as e: 
      print(e)
      if tree is None: 
        abort(404)
      abort(422)
    
  # Error Handling
  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable"
      }), 422


  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "resource not found"
      }), 404
    
  @app.errorhandler(401)
  def unauthorized(error):
      return jsonify({
          "success": False,
          "error": 401,
          "message": "unauthorized action"
      }), 401

  @app.errorhandler(AuthError)
  def auth_found(error):
      return jsonify({
          "success": False,
          "error": AuthError,
          "message": "authentication error"
      }), AuthError

  return app

app = create_app()