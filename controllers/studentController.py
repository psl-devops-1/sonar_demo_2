import logging
from flask import(
    Blueprint,  render_template,
    redirect,
    url_for,
    session,jsonify,
    request,
    flash
)

from config.auth import roleRequired
from config.auth import wantsJson



logger = logging.getLogger(__name__)

studentBp = Blueprint(
    "student",
    __name__,
    url_prefix="/student"
)





@studentBp.route("/dashboard")
@roleRequired("student")
def dashboard():
    try:
        userId = session.get("user_id")
        if wantsJson():
            return jsonify({
                "success": True,
                "message": "Student Dashboard",
                "user_id": session.get("user_id"),
                "role": session.get("role")
            })

        return render_template(
            "studentDashboard.html"
        )
    except ValueError as ve:
        if wantsJson():
            return jsonify({
                "success": False,
                "message": "str(e)"
            }), 400

        return str(e), 400
            
    except Exception as e:
        if wantsJson():
            return jsonify({
                "success": False,
                "message": "Unable to load student dashboard"
            }), 500

        return "Unable to load dashboard", 500

    
   