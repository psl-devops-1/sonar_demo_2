import logging
from flask import(
    Blueprint, make_response,  render_template,
    redirect,
    url_for,
   jsonify,
    request,
    flash
)
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies
)

from forms.authForms import(
    RegisterForm,
    LoginForm
)

from config.auth import wantsJson

from services.userService import UserService

logger = logging.getLogger(__name__)

authBp = Blueprint(
    "auth",
    __name__
)

userService = UserService()

@authBp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = userService.register(
                name=form.name.data,
                email=form.email.data,
                password=form.password.data
            )
            logger.info("User registered successfully: %s", form.email.data)

            if wantsJson():
                return jsonify({
                    "success": True,
                    "message": "Registration successful",
                    "user": 
                       user.toDict()
                    
                }), 201

            flash(
                "Registration successful. Please Login",
                "success"

            )
            return redirect(
                url_for("auth.login")
            )


        except ValueError as ve:
            logger.warning("registration validation failed for %s"
            , form.email.data)
            if wantsJson():
                return jsonify({
                    "success": False,
                    "message": str(ve)
                }), 400
            flash(str(ve), "danger")

        except Exception as e:
            logger.exception("Unexpected error during user registration for %s.", form.email.data)
            if wantsJson():
                return jsonify({
                    "success": False,
                    "message": str(e)
                }), 400
            flash("An unexpected error occurred", "danger")

    if request.method == "POST" and wantsJson():
        logger.warning("Form validation failed on register: %s", form.errors)
        return jsonify({
            "success": False,
            "errors": form.errors
        }), 400

    return render_template(
        "auth/register.html",
        form=form
    )


@authBp.route(
        "/login",
        methods=["GET", "POST"]
)
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = userService.authenticate(
            form.email.data,
            form.password.data
        )

        if not user:
            if wantsJson():
                return jsonify({
                    "success": False,
                    "message": "Invalid email or password"
                }), 401

            flash(
                "Invalid email or password",
                "danger"
            )

            return render_template(
                "auth/login.html",
                form=form
            )

        roleName = user.role.role_name.lower() if user.role else "student"
        additionalClaims = {
            "role": roleName,
            "name": user.name,
            "email":user.email
        }

        accessToken = create_access_token(
            identity=str(user.id),
            additional_claims=additionalClaims
        )

        if wantsJson():
            return jsonify({

                "success": True,
                "message": "Login successful",
                "accessToken": accessToken,
                "user": 
                   user.toDict()
                
            }), 200

        """         if roleName == "admin":
            targetUrl = url_for("admin.dashboard")
            

        elif roleName == "instructor":
            targetUrl =  url_for("instructor.dashboard")
       

        else:
            targetUrl = url_for("student.dashboard") """

        targetUrl = url_for("dashboard.dashboard")

        response = make_response(redirect(targetUrl))
        set_access_cookies(response, accessToken)
        return response
       

    if request.method == "POST" and wantsJson():
        return jsonify({
            "success": False,
            "errors": form.errors
        }), 400

    return render_template(
        "auth/login.html",
        form=form
    )

@authBp.route("/logout", methods=["POST", "GET"])
def logout():
    
    if wantsJson():
        response = make_response(jsonify({
            "success": True,
            "message": "Logged Out"
        }))

        unset_jwt_cookies(response)
        return  response

    response = make_response(redirect(url_for("auth.login")))
    unset_jwt_cookies(response)
    flash("Logged out successfully", "info")
    return response


