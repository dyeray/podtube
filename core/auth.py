from functools import wraps

from flask import request, abort

from core.config import Config


def require_auth(view):
    @wraps(view)
    def wrapper_func(*args, **kwargs):
        required_api_key = Config.get_required_api_key()
        request_api_key = request.args.get("api_key")
        if required_api_key is None or required_api_key == request_api_key:
            return view(*args, **kwargs)
        else:
            abort(401)
    return wrapper_func
