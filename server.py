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

