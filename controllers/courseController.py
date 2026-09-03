import logging
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    jsonify,
    request,
    flash
)


from forms.courseForms import CourseForm, CourseUpdateForm
from dao.courseDao import CourseDao
from services.courseService import CourseService
from config.auth import wantsJson, loginRequired, roleRequired


logger = logging.getLogger(__name__)

courseBp = Blueprint(
    "course",
    __name__
)


courseDao = CourseDao()
courseService = CourseService(courseDao)


@courseBp.route("/courses", methods=["GET"])
@loginRequired
def listCourses():
    courses =  courseService.getAllCourses()

    if wantsJson():
        return jsonify({
            "success": True,
            "courses": [course.toDict() for course in courses]
        })


    return render_template(
        "course/courseList.html",
        courses=courses
    )

@courseBp.route("/courses/<int:courseId>", methods=["GET"])
@loginRequired
def getCourse(courseId):
    try:
        course = courseService.getCourseById(courseId)
        if wantsJson():
            return jsonify({
                "success": True,
                "course": course.toDict()
            })

        return render_template(
            "course/courseDetail.html",
            course=course,
            instructors=course.instructors
        )

    except ValueError as ve:
        logger.warning("Course lookup failed for id %s: %s", courseId,
                        str(ve))
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(ve)
            }), 404

        flash(str(ve), "danger")
        return redirect(url_for("course.listCourses"))


    except Exception as e:
        logger.exception("Unexpected error fetching course %s: error: %s", courseId, str(e))
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400


        flash("An unexpected error occured", "danger")
        return redirect(url_for("course.listCourses"))


@courseBp.route("/courses/create", methods=["GET", "POST"])
@roleRequired("admin")
def createCourse():
    form = CourseForm()

    if form.validate_on_submit():
        try:
            course = courseService.createCourse(
                courseName=form.courseName.data,
                description=form.description.data
            )
            logger.info("Course created successfully: %s", course.course_name)

            if wantsJson():
                return jsonify({
                    "success": True,
                    "message": "Course created successfully",
                    "course": course.toDict()
                }), 201

            flash("Course created successfully", "success")
            return redirect(url_for("course.listCourses"))


        except ValueError as ve:
            logger.warning("Course creation validation failded: %s", str(ve))
            if wantsJson():
                return jsonify({
                    "success": False,
                    "message": str(ve)
                }), 400

            flash(str(ve), "danger")


        except Exception as e:
            logger.exception("Unexpeccted error during course creation")
            if wantsJson():
                return jsonify({
                    "success": False,
                    "message": str(e)
                }), 400

            flash("An unexpected error occurred", "danger")


    if request.method == "POST" and wantsJson():
        logger.warning("Form validation failed on course creation: %s", form.errors)
        return jsonify({
            "success": False,
            "errors": form.errors
        }), 400


    return render_template(
        "course/courseForm.html",
        form=form
    )


@courseBp.route("/courses/<int:courseId>/update", methods=["GET", "POST"])
@roleRequired("admin")
def updateCourse(courseId):

    try:
        course  = courseService.getCourseById(courseId)

        if request.method == "GET":
            form = CourseUpdateForm(
                courseName=course.course_name,
                description=course.description
            )
        else:
            form = CourseUpdateForm()
        
   

        if form.validate_on_submit():
           
            course = courseService.updateCourse(
                courseId,
                courseName=form.courseName.data,
                description=form.description.data
            )

            logger.info("Course updated successfully: %s", course.course_name)


            if wantsJson():
                return jsonify({
                    "success": True,
                    "message": "Course updated successfully",
                    "course": course.toDict()
                })

            flash("Course updated successfully", "success")
            return redirect(url_for("course.getCourse", courseId=course.id))


        

    except ValueError as ve:
        logger.warning("Course update validationf failed for id %s: %s", courseId, str(ve))
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(ve)
            }), 400

        flash(str(ve), "danger")
        return redirect(url_for("course.listCourses"))


    except Exception as e:
        logger.exception("Unexpected error during course update for id %s", courseId)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400
        flash("An unexpected error occured", "danger")
        return redirect(url_for("course.listCourses"))



    if request.method == "POST" and wantsJson():
        logger.warning("Form validation failed on course update: %s", form.errors)
        return jsonify({
            "success": False,
            "errors": form.errors
        }), 400


    return render_template(
        "course/courseForm.html",
        form=form
    )



@courseBp.route("/courses/<int:courseId>/delete", methods=["POST"])
@roleRequired("admin")
def deleteCourse(courseId):
    try:
        courseService.deleteCourse(courseId)
        logger.info("Course delted successfully: %s", courseId)

        if wantsJson():
            return jsonify({
                "success": True,
                "message": "Course deleted successfully"
        })

        flash("Course deleted successfully", "success")

    except ValueError as ve:
        logger.warning("Course deletion failed for id %s", courseId)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(ve)
            }), 404

        flash(str(ve), "danger")



    except Exception as e:
        logger.exception("Unexpected error during course deletion for id %s", courseId)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

        flash("An unexpected error occured", "danger")


    return redirect(url_for("course.listCourses"))
        

    