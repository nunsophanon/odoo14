from odoo import http
from odoo.http import request, Response
import base64
import werkzeug.wrappers
import json
import datetime
import functools
import os
import jwt

PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDF+EP25cmCyCX6\n0ilFneMmYGE7g93vzI0QPMz8jVhHWZgpmSZESHmEQHrt07+6VQqN0HCsuiZar8mE\necE1CnT1T7+0movBdLxWhjExvqkhyBTGjgIF3Tnfl5YWcvIyce/Uh0KITPffcNDB\njCrTSBNu2P/f8/1B+44vkV0s/Bo7tR0fNRFVJ/JazxLgy/C39wyAIn5tTh9UMbM5\nnYOpRP8YuSa9ydnerbfFcj9cX/bXGLyZNNFMI1/36hiziZ8j9nxf7B6B5ZqQYLPR\n5hrkPJY8zUMq8JEPXm8fFIQiWldIHC94aS81lgbEyBaWjgDckI5CUy2B8At1xOPd\n7lDFnO/hAgMBAAECggEAF9cjNiUrfHqmajtrWXUfUPSL2QszC6j+Nt2fkO1jm2oM\nczv8ef4hVh4ev6u/m8yYcgYPP5nGOycOtUulSwIong8dxr3SxTgN4zyTSYqMmyMZ\nb2TUFQk0ajr6ydbLWGxUpaspRblBI3EWTqyWzq1QG8n5nGppTgwhbhSLHDr63MQn\nLlXC/hi25CwzKFnuuAHTGQplu9aQ6XQGy2NRdIUl9vbLX8+8DGiIaEBPua//MJiQ\naZ2CNS5pX55rSJM2FqjDcLg+mr4YH7VTxEnCeWdssDkxL486wilLi7bspxFCjF3E\nptMqCFfmH9ml2I64RgmQA1QFZGQSe9RLzoopyvj3MQKBgQDy2duY1/m1a+XVGzFB\nJAgmKJgileV2MIJbDf9bY8FvVboT/VqJWOg4cZl1DY4DlIZGkCxv4Cht6bsh++as\n9utfwMY2sH8in37Zycpx1VgGIsBUfGANNN/Tu4D8cLtwAjAchLla9pvBZa1SE3SI\ntskRLsplg7WVzjaAQ47U2yh0mQKBgQDQsE/d6FIvxH0ieX8MH0v/kvkdG+XPcElh\nD5SgPp4iz4hutwZL64PmVn3QTPbJSrSd6R4N27SKHESNvEyqrExQmB6Wr4WH+rIr\nlyl2PZCOdXpN6qHbxOPNqGA6Mbunqx1vLNBstyBFlymyzZKLpFQ24Nm+oTmQQ5nZ\n4Z8fXncaiQKBgQC/HD65+0yhPrXxjKKoNqjLDqsanIelCOusqElKLCivavEyhfBX\nocWtlYhEG1Sk8J7yrMari+WFCaigR9HyT6ZPBi92HlMOdiGnViughVnuCi78zZvx\nCKkTwLzy6+w1ayNdbf1H3kYYXeGVc4YDiISWpxHT7WBa8ZrmOUQPsiAWEQKBgGWh\nN4PuG/g/TGF5obGZnD0+qirO5z/6gwHNwKe5VvHE98BTSbG3ZGjMPkEu+hBVXVh5\nqrU9BdMsqQYNaZjEh/XH3z2rBPCP2iz4VKzMlpWKCKHhXinU3MvO7+3nQmgJITB/\nNpF7LTA2yYvWKUPwJ0MChYgcpBfplAdTpVZ1frNhAoGAdsgpZNXHJt/CZYrV5RnE\nor0QDSqKExPntjqEKv1TZnikFYLVaUasGH+p+JqB8ziaKl16OPcQkEzxLys5XP+A\nkUWsqXQSoB9+7Id2w3CyfhGW/GUnmpApSujILTlNLpiRdjpTTXLRFqYmOJ8LiKUP\nqVeKEx7uR8PiSB7cfOWZV6M=\n-----END PRIVATE KEY-----\n"


def valid_response_http(data, status=200):
    """Valid Response
    This will be return when the http request was successfully processed."""
    Response.status=str(status)
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
    Response.status=str(status)
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
    This will be return when the http request was successfully processed."""
    # return werkzeug.wrappers.Response(
    #     status=status,
    #     content_type="application/json; charset=utf-8",
    #     response=json.dumps(data, default=datetime.datetime.isoformat),
    # )
    Response.status=str(status)
    return data


def invalid_response(type, message=None, status=401):
    """Invalid Response
    This will be the return value whenever the server runs into an error
    either from the client or the server."""
    # return json.dumps({})
    # return werkzeug.wrappers.Response(
    #     status=status,
    #     content_type="application/json; charset=utf-8",
    #     response=json.dumps(
    #         {
    #             "type": type,
    #             "message": str(message)
    #             if str(message)
    #             else "wrong arguments (missing validation)",
    #         },
    #         default=datetime.datetime.isoformat,
    #     ),
    # )
    Response.status=str(status)
    return message


def validate_token(function):

    @functools.wraps(function)
    def wrap_validate_token(self, *args, **kwargs):
        """."""
        client_token = request.httprequest.headers.get("Authorization")
        # client_id = request.httprequest.headers.get('client_id')
        if not client_token:
            return invalid_response(
                "Client Token not found", "Missing Token in request header", 401
            )

        # if not client_id:
        #     return invalid_response(
        #         "Client ID not found", "Missing Client ID in request header", 401
        #     )

        secret = request.env['ir.config_parameter'].sudo().get_param('mobile.api.key')
        key = "Bearer "+secret

        if client_token != key:
            return invalid_response("Token Error", "Access Token seems to have expired or invalid", 401)

        # request.session.uid = client_id
        user = request.env['res.users'].sudo().search([('login', '=', 'admin')],limit=1)
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
def validate_jwt(function):
    @functools.wraps(function)
    def wrap_validate_jwt(self, *args, **kwargs):
        token = request.httprequest.headers.get("accessToken")
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

        return function(self, *args, **kwargs, uid=decoded['user_id'])
    return wrap_validate_jwt
