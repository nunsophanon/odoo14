import odoo
from odoo import api, fields, models, http, modules, _
from odoo.http import request
from odoo.addons.accounting_api.controller.helper import validate_token, validate_jwt, get_table_model, valid_response, invalid_response, valid_response_http, invalid_response_http
import json
import math
import jwt
PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDF+EP25cmCyCX6\n0ilFneMmYGE7g93vzI0QPMz8jVhHWZgpmSZESHmEQHrt07+6VQqN0HCsuiZar8mE\necE1CnT1T7+0movBdLxWhjExvqkhyBTGjgIF3Tnfl5YWcvIyce/Uh0KITPffcNDB\njCrTSBNu2P/f8/1B+44vkV0s/Bo7tR0fNRFVJ/JazxLgy/C39wyAIn5tTh9UMbM5\nnYOpRP8YuSa9ydnerbfFcj9cX/bXGLyZNNFMI1/36hiziZ8j9nxf7B6B5ZqQYLPR\n5hrkPJY8zUMq8JEPXm8fFIQiWldIHC94aS81lgbEyBaWjgDckI5CUy2B8At1xOPd\n7lDFnO/hAgMBAAECggEAF9cjNiUrfHqmajtrWXUfUPSL2QszC6j+Nt2fkO1jm2oM\nczv8ef4hVh4ev6u/m8yYcgYPP5nGOycOtUulSwIong8dxr3SxTgN4zyTSYqMmyMZ\nb2TUFQk0ajr6ydbLWGxUpaspRblBI3EWTqyWzq1QG8n5nGppTgwhbhSLHDr63MQn\nLlXC/hi25CwzKFnuuAHTGQplu9aQ6XQGy2NRdIUl9vbLX8+8DGiIaEBPua//MJiQ\naZ2CNS5pX55rSJM2FqjDcLg+mr4YH7VTxEnCeWdssDkxL486wilLi7bspxFCjF3E\nptMqCFfmH9ml2I64RgmQA1QFZGQSe9RLzoopyvj3MQKBgQDy2duY1/m1a+XVGzFB\nJAgmKJgileV2MIJbDf9bY8FvVboT/VqJWOg4cZl1DY4DlIZGkCxv4Cht6bsh++as\n9utfwMY2sH8in37Zycpx1VgGIsBUfGANNN/Tu4D8cLtwAjAchLla9pvBZa1SE3SI\ntskRLsplg7WVzjaAQ47U2yh0mQKBgQDQsE/d6FIvxH0ieX8MH0v/kvkdG+XPcElh\nD5SgPp4iz4hutwZL64PmVn3QTPbJSrSd6R4N27SKHESNvEyqrExQmB6Wr4WH+rIr\nlyl2PZCOdXpN6qHbxOPNqGA6Mbunqx1vLNBstyBFlymyzZKLpFQ24Nm+oTmQQ5nZ\n4Z8fXncaiQKBgQC/HD65+0yhPrXxjKKoNqjLDqsanIelCOusqElKLCivavEyhfBX\nocWtlYhEG1Sk8J7yrMari+WFCaigR9HyT6ZPBi92HlMOdiGnViughVnuCi78zZvx\nCKkTwLzy6+w1ayNdbf1H3kYYXeGVc4YDiISWpxHT7WBa8ZrmOUQPsiAWEQKBgGWh\nN4PuG/g/TGF5obGZnD0+qirO5z/6gwHNwKe5VvHE98BTSbG3ZGjMPkEu+hBVXVh5\nqrU9BdMsqQYNaZjEh/XH3z2rBPCP2iz4VKzMlpWKCKHhXinU3MvO7+3nQmgJITB/\nNpF7LTA2yYvWKUPwJ0MChYgcpBfplAdTpVZ1frNhAoGAdsgpZNXHJt/CZYrV5RnE\nor0QDSqKExPntjqEKv1TZnikFYLVaUasGH+p+JqB8ziaKl16OPcQkEzxLys5XP+A\nkUWsqXQSoB9+7Id2w3CyfhGW/GUnmpApSujILTlNLpiRdjpTTXLRFqYmOJ8LiKUP\nqVeKEx7uR8PiSB7cfOWZV6M=\n-----END PRIVATE KEY-----\n"


class AccountingAPI(http.Controller):

    @validate_token
    @http.route('/accounting/login', type="http", auth="none", methods=["GET", "POST"], csrf=False)
    def get_jwt_token(self, **payload):
        login = payload.get("username", False)
        password = payload.get("password", False)
        try:
            uid = request.session.authenticate(request.session.db, login, password)
            to_be_encoded = {
                'user_id': uid
            }
            encoded_jwt = jwt.encode(to_be_encoded, PRIVATE_KEY, algorithm='HS256').decode('utf-8')
            return valid_response_http({"accessToken": encoded_jwt})
        except odoo.exceptions.AccessDenied as e:
            request.uid = 1
            if e.args == odoo.exceptions.AccessDenied().args:
                message = _("Wrong Username/password")
            else:
                message = e.args[0]
        return invalid_response_http(type="Login error", message=message, status=403)

    @validate_token
    @validate_jwt
    @http.route('/accounting/get_accounts', type="http", auth="none", methods=["GET"], csrf=False)
    def get_accounts(self, **payload):
        try:
            accounts = request.env['account.account'].sudo().search([])
            account_lists = []
            for account in accounts:
                account_lists.append({
                    "id": account.id,
                    "code":account.code,
                    "name": account.name,
                })
            return valid_response_http(account_lists)
        except:
            message = _("Error during get Account model. Please contact to administrator.")
        return invalid_response_http(type="Getting Accounts Error", message=message, status=403)

    @validate_token
    @validate_jwt
    @http.route('/accounting/get_journals', type="http", auth="none", methods=["GET"], csrf=False)
    def get_journals(self, **payload):
        try:
            journals = request.env['account.journal'].sudo().search([])
            journal_lists = []
            for journal in journals:
                journal_lists.append({
                    "id": journal.id,
                    "name": journal.name,
                })
            return valid_response_http(journal_lists)
        except:
            message = _("Error during get Journal model. Please contact to administrator.")
        return invalid_response_http(type="Getting Journal Error", message=message, status=403)

    @validate_token
    @validate_jwt
    @http.route('/accounting/post_journal_entries', type="http", auth="none", methods=["GET"], csrf="False")
    def post_journal_entries(self, uid, **payload):
        values = payload.get("values", False)
        if values:
            journal_data = json.loads(values)
        try:
            print()
            account_move_obj = request.env['account.move'].sudo()
            account_move_id = account_move_obj.create(journal_data)
            return valid_response_http(data={"account_move_id": account_move_id.id},status=200)
        except Exception as e:
            message = str(e)
        return invalid_response_http(type="Posting Journal Entries Failed", message=message, status=403)

    @validate_token
    @validate_jwt
    @http.route('/accounting/update_journal_entry', type="http", auth="none", methods=["post"], csrf=False)
    def update_journal_entries(self, uid, **payload):
        journal_id = payload.get("id", False)
        values = payload.get("values", False)
        if values:
            journal_data = json.loads(values)
        if journal_id:
            try:
                account_move = get_table_model('account.move').search([('account_move_id', '=', journal_id)])
                account_move.write(values)
                return valid_response_http(data='success', status=200)
            except:
                message = _("Journal Entry Not Found. Please contact to administrator.")
        else:
            message = _("Journal Entry is Missing")
        return invalid_response_http(type="Update Journal Entry error", message=message, status=403)
