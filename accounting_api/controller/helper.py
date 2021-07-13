from odoo import http, SUPERUSER_ID
from odoo.http import request, Response
from odoo.tools import frozendict
import werkzeug.wrappers
import json
import googlemaps
import datetime
import functools
import jwt
import ctypes
import logging
import hashlib
import os.path
from ctypes import *
from requests.auth import HTTPBasicAuth
_logger = logging.getLogger(__name__)

def get_gmaps_distance(key, source, destination):
    try:
        res = googlemaps.Client(key).distance_matrix(source, destination)['rows'][0]['elements'][0]
        if res.get("status","") == "OK":
            return res["distance"]["value"]
        return 999999999
    except:
        _logger.warning('Google Map Api Key Error')
        return 999999999

try:
    current_dir = os.path.abspath(os.path.dirname(__file__))
    lib = ctypes.cdll.LoadLibrary(os.path.join(current_dir, "myaes.so"))
    # lib = ctypes.cdll.LoadLibrary("/home/odoo/src/user/mobile_api/controller/myaes.so")
    # lib = ctypes.cdll.LoadLibrary("./myaes.so")
    lib.myaes_encrypt.restype = c_char_p
    lib.myaes_encrypt.argtypes = [c_char_p]
    lib.myaes_decrypt.restype = c_char_p
    lib.myaes_decrypt.argtypes = [c_char_p]

    def huione_encrypt(payload):
        """ Huione Encrypt
        This will be return encrypted string when the json_str was successfully encrypt.
        @param payload: json to be decrypt
        """
        return lib.myaes_encrypt(json.dumps(payload, sort_keys=True, separators=(',', ': ')).encode('utf-8')).decode()

    def huione_decrypt(string):
        """ Huione Decrypt
        This will be return data as dict when the json_str was successfully decrypt
        @param string: json string to be decrypt
        """
        return json.loads(lib.myaes_decrypt(string.encode('utf-8')))

    def huione_md5(string):
        """ Huione API auth
        This will be return basic auth for used to request to huione.
        @param string: string
        """
        return hashlib.md5(string.encode('utf-8')).hexdigest()

    def huione_auth(username, password):
        """ Huione API auth
        This will be return basic auth for used to request to huione.
        @param username: string
        @param password: string
        """
        return HTTPBasicAuth(username, huione_md5(password))
except:
    _logger.warning('Huione: This Library only Support in Ubuntu. Huione method is not working')

def valid_response_http(data, status=200):
    """Valid Response
    This will be return when the http request was successfully processed."""
    return Response(
        status=status,
        content_type="application/json; charset=utf-8",
        response=json.dumps(data, default=datetime.datetime.isoformat),
    )


def invalid_response_http(type, message=None, status=401):
    """Invalid Response
    This will be the return value whenever the server runs into an error
    either from the client or the server."""
    # return json.dumps({})
    return Response(
        status=status,
        content_type="application/json; charset=utf-8",
        response=json.dumps(
            {
                "type": type,
                "message": str(message)
                if str(message)
                else "wrong arguments (missing validation)",
            },
            default=datetime.datetime.isoformat,
        ),
    )


def valid_response(data, status=200):
    """Valid Response
    This will be return when the json request was successfully processed."""
    return data


def invalid_response(type, message=None, status=401):
    """Invalid Response
    This will be the return value whenever the server runs into an error
    either from the client or the server."""
    raise werkzeug.exceptions.NotFound({
        "mobile_api": True,
        "type": type,
        "message": str(message) if str(message) else "wrong arguments (missing validation)",
        "http_status": status
    })


def validate_token(function):
    @functools.wraps(function)
    def wrap_validate_token(self, *args, **kwargs):
        """."""
        client_token = request.httprequest.headers.get("Authorization")
        if not client_token:
            return invalid_response(
                "Client Token not found", "Missing Token in request header", 401
            )

        secret = request.env['ir.config_parameter'].sudo().get_param('accounting.api.key')
        key = "Bearer " + secret

        if client_token != key:
            return invalid_response("Token Error", "Access Token seems to have expired or invalid", 401)

        user = request.env['res.users'].sudo().browse(SUPERUSER_ID).exists()
        if not user:
            user = request.env['res.users'].sudo().search([], limit=1)
        request.env.user = user
        request.env.company = user.company_id
        request.website = request.env['website'].get_current_website()
        return function(self, *args, **kwargs)

    return wrap_validate_token


def get_table_model(table_name: str):
    """return a table model for accessing database

    Arguments:
        table_name {str} -- specify table name

    Returns:
        model -- table model
    """
    return http.request.env[table_name].sudo()

# Validate whether jwt is valid or not
def validate_register_jwt(function):
    @functools.wraps(function)
    def wrap_validate_jwt(self, *args, **kwargs):
        token = request.httprequest.headers.get("registerToken")
        PRIVATE_KEY = request.env['ir.config_parameter'].sudo().get_param('mobile.server.private.key')
        if not token:
            return invalid_response("Register Token Error", "Missing Register Token", 401)
        try:
            jwt_token = token.split()[1]
            decoded = jwt.decode(jwt_token, PRIVATE_KEY, algorithms='HS256')
        except jwt.exceptions.ExpiredSignatureError:
            return invalid_response(
                "Register Token Error", "Register Token is expired", 401
            )
        except jwt.exceptions.InvalidTokenError:
            return invalid_response(
                "Register Token Error", "Register Token is invalid", 401
            )
        except jwt.exceptions.DecodeError:
            return invalid_response(
                "Register Token Error", "Register Token is error while decoding", 401
            )
        except:
            return invalid_response(
                "Register Token Error", "Register Token is invalid", 401
            )

        user = request.env['res.users'].sudo().browse(SUPERUSER_ID).exists()
        if not user:
            user = request.env['res.users'].sudo().search([], limit=1)
        request.env.user = user
        request.env.company = user.env.company.search([], limit=1)
        return function(self, *args, **kwargs, phone=decoded['phone'], password=decoded['password'], ip=decoded['ip'],
                        application_id=decoded['application_id'], name=decoded['name'])
    return wrap_validate_jwt

# Validate whether jwt is valid or not
def validate_pw_jwt(function):
    @functools.wraps(function)
    def wrap_validate_jwt(self, *args, **kwargs):
        token = request.httprequest.headers.get("resetToken")
        PRIVATE_KEY = request.env['ir.config_parameter'].sudo().get_param('mobile.server.private.key')
        if not token:
            return invalid_response("Reset Token Error", "Missing Reset Token", 401)
        try:
            jwt_token = token.split()[1]
            decoded = jwt.decode(jwt_token, PRIVATE_KEY, algorithms='HS256')
        except jwt.exceptions.ExpiredSignatureError:
            return invalid_response(
                "Reset Token Error", "Reset Token is expired", 401
            )
        except jwt.exceptions.InvalidTokenError:
            return invalid_response(
                "Reset Token Error", "Reset Token is invalid", 401
            )
        except jwt.exceptions.DecodeError:
            return invalid_response(
                "Reset Token Error", "Reset Token is error while decoding", 401
            )
        except:
            return invalid_response(
                "Reset Token Error", "Reset Token is invalid", 401
            )

        user = request.env['res.users'].sudo().browse(decoded['user_id'])
        request.uid = user.id
        request.env.user = user
        request.env.company = user.env.company.search([], limit=1)
        return function(self, *args, **kwargs, uid=decoded['user_id'], code=decoded['code'])

    return wrap_validate_jwt

# Validate whether jwt is valid or not
def validate_jwt(function):
    @functools.wraps(function)
    def wrap_validate_jwt(self, *args, **kwargs):
        token = request.httprequest.headers.get("accessToken")
        PRIVATE_KEY = request.env['ir.config_parameter'].sudo().get_param('accounting.server.private.key')
        if not token:
            return invalid_response("Access Token Error", "Missing Access Token", 401)
        try:
            jwt_token = token.split()[1]
            decoded = jwt.decode(jwt_token, PRIVATE_KEY, algorithms='HS256')
        except jwt.exceptions.ExpiredSignatureError:
            return invalid_response(
                "Access Token Error", "Access Token is expired", 401
            )
        except jwt.exceptions.InvalidTokenError:
            return invalid_response(
                "Access Token Error", "Access Token is invalid", 401
            )
        except jwt.exceptions.DecodeError:
            return invalid_response(
                "Access Token Error", "Access Token is error while decoding", 401
            )
        except:
            return invalid_response(
                "Access Token Error", "Access Token is invalid", 401
            )

        user = request.env['res.users'].sudo().browse(decoded['user_id'])
        context = request._context.copy()
        if user.lang:
            context.update({
                'lang': user.lang
            })
        request._context = frozendict(context)
        request.uid = user.id
        request.env.user = user
        request.env.company = user.company_id
        if not user.company_id:
            request.env.company = user.env.company.search([], limit=1)
        request.website = request.env['website'].get_current_website()
        return function(self, *args, **kwargs, uid=decoded['user_id'])

    return wrap_validate_jwt