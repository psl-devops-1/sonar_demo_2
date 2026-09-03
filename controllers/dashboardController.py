import logging

from flask import (
    Blueprint,
    render_template
)

from flask_jwt_extended import get_jwt

from config.auth import loginRequired


logger = logging.getLogger(__name__)


dashboardBp = Blueprint(
    "dashboard",
    __name__
)


@dashboardBp.route("/dashboard", methods=["GET"])
@loginRequired
def dashboard():

    try:
        claims = get_jwt()

        role = claims.get("role", "").lower()

        if role == "admin":
            return render_template(
                "dashboard/adminDashboard.html"
            )

        if role == "instructor":
            return render_template(
                "dashboard/instructorDashboard.html"
            )

        if role == "student":
            return render_template(
                "dashboard/studentDashboard.html"
            )

        logger.warning(
            "Unknown role attempting to access dashboard: %s",
            role
        )

        return "Forbidden", 403

    except Exception:
        logger.exception(
            "Unexpected error while loading dashboard"
        )
        return "An unexpected error occurred", 500