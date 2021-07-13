import odoo
import logging
import werkzeug
from odoo.http import AuthenticationError, SessionExpiredException, serialize_exception
import json
from odoo.http import JsonRequest


_handle_exception = JsonRequest._handle_exception  # original json _handle_exception method

_logger = logging.getLogger(__name__)

def _handle_exception(self, exception):
    """Called within an except block to allow converting exceptions
           to arbitrary responses. Anything returned (except None) will
           be used as response."""
    try:
        data = exception.description
        if isinstance(data,dict) and data.get('mobile_api',False):
            data.pop('mobile_api')
            return self._json_response(error=data)
    except:
        pass

    try:
        return super(JsonRequest, self)._handle_exception(exception)
    except Exception:
        if not isinstance(exception, SessionExpiredException):
            if exception.args and exception.args[0] == "bus.Bus not available in test mode":
                _logger.info(exception)
            elif isinstance(exception, (odoo.exceptions.UserError,
                                        werkzeug.exceptions.NotFound)):
                _logger.warning(exception)
            else:
                _logger.exception("Exception during JSON request handling.")
        error = {
            'code': 200,
            'message': "Odoo Server Error",
            'data': serialize_exception(exception),
        }
        if isinstance(exception, werkzeug.exceptions.NotFound):
            error['http_status'] = 404
            error['code'] = 404
            error['message'] = "404: Not Found"
        if isinstance(exception, AuthenticationError):
            error['code'] = 100
            error['message'] = "Odoo Session Invalid"
        if isinstance(exception, SessionExpiredException):
            error['code'] = 100
            error['message'] = "Odoo Session Expired"
        return self._json_response(error=error)

JsonRequest._handle_exception = _handle_exception