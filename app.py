import os
from flask import Flask, request, abort, jsonify, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, distinct
from flask_cors import CORS
import json
from auth import requires_auth, AuthError
from models import setup_db, database_path, Tree, Farmer, Forest, db
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
from dotenv import load_dotenv, find_dotenv
from werkzeug.exceptions import HTTPException


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    oauth = OAuth(app)
    CORS(app)
    setup_db(app, database_path)
    app.secret_key = os.environ.get("SECRET_KEY")

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')

        return response

    auth0 = oauth.register(
        'auth0',
        client_id='oKWhbpnbNRWsmcY52NgNmbTSTnEyr7vA',
        client_secret=os.environ.get("CLIENT_SECRET"),
        api_base_url='https://tree-app.eu.auth0.com',
        access_token_url='https://tree-app.eu.auth0.com/oauth/token',
        authorize_url='https://tree-app.eu.auth0.com/authorize',
        client_kwargs={
            'scope': 'openid profile email',
        },
    )

    @app.route('/callback')
    def callback_handling():
        # Handles response from token endpoint
        auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()

        # Store the user information in flask session.
        session['jwt_payload'] = userinfo
        session['profile'] = {
            'user_id': userinfo['sub'],
            'name': userinfo['name'],
            'picture': userinfo['picture']
        }
        return redirect('/')

    @app.route('/login')
    def login():
        return auth0.authorize_redirect(
            redirect_uri='https://tree-app-udacity.herokuapp.com/')

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
            'forests': forests,
            'number_of_forests': len(forests)
        })

    # GET FARMERS
    @app.route('/farmers', methods=['GET'])
    def get_farmers():
        farmers = [farmer.format() for farmer in Farmer.query.all()]
        return jsonify({
            'success': True,
            'farmers': farmers,
            'number_of_farmers': len(farmers)
        })

    # GET ONE FARMER
    @app.route('/farmers/<int:id>', methods=['GET'])
    def get_farmer_id(id):
        farmer = Farmer.query.filter(Farmer.id == id).one_or_none()
        if farmer is None:
            abort(404)

        # Getting tree count by type for selected farmer
        farmer_trees_by_type_query = db.session.query(
            Tree.name,
            func.count(
                Tree.id).label('count')).filter(
            Tree.farmer_id == id).group_by(
                Tree.name)
        tree_count_by_type = {
            row.name: row.count for row in farmer_trees_by_type_query}

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
        forest_trees_by_type_query = db.session.query(
            Tree.name,
            func.count(
                Tree.id).label('count')).filter(
            Tree.forest_id == id).group_by(
                Tree.name)
        tree_count_by_type = {
            row.name: row.count for row in forest_trees_by_type_query}

        # Getting number of farmers for selected forest
        farmer_count_query = db.session.query(
            func.count(
                distinct(
                    Tree.farmer_id))).filter(
            Tree.forest_id == id)
        # try/except block to get the count of unique farmers - better way to
        # do this??
        try:
            farmer_count = farmer_count_query[0][0]
        except BaseException:
            farmer_count = 0

        return jsonify({
            'success': True,
            'forest': forest.format(),
            'trees': tree_count_by_type,
            'number_of_trees': len(forest.get_trees()),
            'farmer_count': farmer_count
        })

    # CREATE FARMER
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
                "total_farmers": len(Farmer.query.all())
            })

        except Exception as e:
            print(e)
            abort(422)

    # EDIT FARMER
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

    # CREATE TREE
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
            if Farmer.query.filter(id == farmer_id).one_or_none is None:
                print(f'Farmer with id {farmer_id} does not exist')
                abort(404)

            if Forest.query.filter(id == forest_id).one_or_none is None:
                print(f'Forest with id {forest_id} does not exist')
                abort(404)

            trees = []
            for i in range(quantity):
                tree = Tree(
                    name=name,
                    farmer_id=farmer_id,
                    forest_id=forest_id)
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

    # DELETE TREE

    @app.route('/trees/<int:id>', methods=['DELETE'])
    @requires_auth('delete:tree')
    def delete_tree(payload, id):
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

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    @app.errorhandler(AuthError)
    def auth_found(error):
        return jsonify({
            "success": False,
            "error": AuthError,
            "message": "authentication error"
        }), AuthError

    return app


app = create_app()
