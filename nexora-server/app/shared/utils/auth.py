from functools import wraps
from flask import request, g
import jwt

def require_permission(permission):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            if not token:
                return {"error": "Unauthorized"}, 401

            try:
                payload = jwt.decode(token, SECRET, algorithms=["HS256"])
                g.user = payload
                if permission not in payload.get("permissions", []):
                    return {"error": "Forbidden"}, 403
            except jwt.ExpiredSignatureError:
                return {"error": "Token expired"}, 401
            except Exception as e:
                return {"error": "Invalid token"}, 401
            return fn(*args, **kwargs)
        return decorated
    return wrapper
