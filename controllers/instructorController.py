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


instructorBp = Blueprint(
    "instructor",
    __name__,
    url_prefix="/instructor"
)


@instructorBp.route("/dashboard")
@roleRequired("instructor")
def dashboard():
    try:
        userId = session.get("user_id")
        if wantsJson():
            return jsonify({
                "success": True,
                "message": "Instrutor Dashboard",
                "user_id" : userId,
                "role": "instructor"
            })
        return render_template(
            "instructorDashboard.html"
        )
    except ValueError as e:
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400
        return str(e), 400

    except Exception as e:
        if wantsJson():
            return jsonify({
                "success": False,
                "message": "unable to load instructor dashboard"
            }), 500


        return "unable to load instructor dashboard", 500
