from functools import wraps
from flask import request, session, redirect, url_for, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

def loginRequired(viewFunction):
    @wraps(viewFunction)
    def wrappedView(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception as e:
            if wantsJson():
                return jsonify({
                    "success": False,
                    "message": "Authentication required",
                  
                }), 401

            return redirect(url_for("auth.login"))
        
        return viewFunction(*args, **kwargs)

    return wrappedView

def roleRequired(*allowedRoles):
    def decorator(viewFunction):
        @wraps(viewFunction)
        def wrappedView(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                #currentRole = get_jwt()
                currentRole = claims.get("role")

            except Exception:
                if wantsJson():
                    return jsonify({
                        "success": False,
                        "message": "Authentication required"
                    }), 401

                return redirect(url_for("auth.login"))

            normalizedAllowedRoles = [r.lower() for r in allowedRoles]

            if currentRole not in normalizedAllowedRoles:
                if wantsJson():
                    return jsonify({
                        "success": False,
                        "message": "Access Denied"
                    }), 403
                
           
            return  viewFunction(*args, **kwargs)

        return wrappedView
    return decorator

def getCurrentUserIdentity():
    try:
        return get_jwt_identity()
    except Exception:
        return None


def getCurrentUserClaims():
    try:
        return get_jwt()
    except Exception:
        return {}


def wantsJson():
    return request.is_json or  request.accept_mimetypes.best == "application/json"


        
