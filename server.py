from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException
import os
from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
from app import app

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id='oKWhbpnbNRWsmcY52NgNmbTSTnEyr7vA',
    client_secret= os.environ.get("CLIENT_SECRET"),
    api_base_url='https://tree-app.eu.auth0.com',
    access_token_url='https://tree-app.eu.auth0.com/oauth/token',
    authorize_url='https://tree-app.eu.auth0.com/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

# Here we're using the /callback route.
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
    return auth0.authorize_redirect(redirect_uri='https://tree-app-udacity.herokuapp.com/')