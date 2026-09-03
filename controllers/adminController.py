from flask import(
    Blueprint,
    render_template,
    jsonify,
    session
)

from config.auth import (
    roleRequired,
    wantsJson
)

adminBp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)

@adminBp.route("/dashboard")
@roleRequired("admin")
def dashboard():
    try:
        userId = session.get("user_id")
        if wantsJson():
            return jsonify({
                "success": True,
                "message": "Admin Dashboard",
                "user_id": userId,
                "role": "admin"
            })
        return render_template(
            "adminDashbaord.html"
        )

    except ValueError as e:
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

        return str(e), 400

    except Exception:
        if wantsJson():
            return jsonify({
                "success": False,
                "message": "Unablet to load admin dashboard"
            }), 500
        return "Unable to load admin dashboard", 500