

import json
import unittest
import time
import jwt

from project.api.models import BlacklistToken, decode_auth_token
from project.tests.base import BaseTestCase

from flask import current_app


def encode_auth_token(user_id):
    """
    Generates the Auth Token (for testing only)
    returns a string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e





# class TestFileUpload(BaseTestCode):
