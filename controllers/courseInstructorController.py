import logging
from flask import(
    Blueprint,
    render_template,
    redirect,
    url_for,
    jsonify,
    request,
    flash
)

from dao.courseInstructorDao import CourseInstructorDao
from dao.courseDao import CourseDao
from dao.userDao import UserDao
from services.courseInstructorService import CourseInstructorService
from config.auth import getCurrentUserIdentity, wantsJson, loginRequired, roleRequired

logger = logging.getLogger(__name__)
courseInstructorBp = Blueprint("courseInstructor", __name__)

courseInstructorDao = CourseInstructorDao()
courseDao = CourseDao()
userDao = UserDao()
courseInstructorService = CourseInstructorService(courseInstructorDao, courseDao,userDao)


@courseInstructorBp.route(
    "/courses/<int:courseId>/instructors",
    methods=["GET"]
)
@roleRequired("admin", "instructor")
def listInstructors(courseId):

    try:
        assignments = courseInstructorService.getInstructorsByCourseId(
            courseId
        )

        instructors = courseInstructorService.getAvailableInstructors(courseId)

        if wantsJson():
            return jsonify({
                "success": True,
                "instructors": [
                    assignment.toDict()
                    for assignment in assignments
                ]
            })

        return render_template(
            "course/instructorList.html",           
            courseId=courseId,
             assignments=assignments,
             instructors=instructors
        )

    except ValueError as ve:

        logger.warning(
            "Failed to get instructors for course %s: %s",
            courseId,
            str(ve)
        )

        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(ve)
            }), 404

        flash(str(ve), "danger")

        return redirect(
            url_for(
                "course.getCourse",
                courseId=courseId
            )
        )

    except Exception as e:

        logger.exception(
            "Unexpected error getting instructors for course %s",
            courseId
        )

        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

        flash(
            "Unable to load course instructors",
            "danger"
        )

        return redirect(
            url_for(
                "course.getCourse",
                courseId=courseId
            )
        )



@courseInstructorBp.route("/courses/<int:courseId>/instructors", methods=["POST"])
@roleRequired("admin")
def assignInstructors(courseId):
    payload = request.get_json(silent=True) or request.form

    instructorId = payload.get("instructorId")

    try:
        if not instructorId:
            raise ValueError("instructorId is required")

        courseInstructor = courseInstructorService.assignInstructor(courseId,  int(instructorId))
        logger.info("Instructor %s assigned to course %s", instructorId, courseId)



        if wantsJson():
            return jsonify({
                "success": True,
                "message": "Instructor assigned successfully",
                "courseInstructor": courseInstructor.toDict()
            }), 201

        flash("Instructor assigned successfully", "success")
        return redirect(url_for("course.getCourse", courseId=courseId))

    except ValueError as ve:
        logger.warning("Instrucotr assignment failed for course %s", courseId)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(ve)
                
            }), 400

        flash(str(ve), "danger")
        return redirect(url_for("course.getCourse", courseId=courseId))


    except Exception as e:
        logger.exception("Unexpected error assigning instrucotr to course %s", courseId)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

        flash("An unexpected error occurred", "danger")
        return redirect(url_for("course.getCourse", courseId=courseId))




@courseInstructorBp.route("/courses/<int:courseInstructorId>/remove", methods=["POST"])
@roleRequired("admin")
def removeInstructors(courseInstructorId):


    try:
        courseInstructor = courseInstructorService.getCourseInstructorById(courseInstructorId)
        courseId = courseInstructor.course_id
        courseInstructorService.removeInstructor(courseInstructorId)

        logger.info("Removed course instructor assignment %s", courseInstructorId)

        if wantsJson():
            return jsonify({
                "success": True,
                "message": "Instructor removed successfully"
            })

        flash("Instructor removed successfully", "success")
        return redirect(url_for("course.getCourse", courseId=courseId))



    except ValueError as ve:
        logger.warning("Instrucotr removal failed for id %s",courseInstructorId)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(ve)
                
            }), 400

        flash(str(ve), "danger")
        return redirect(url_for("course.listCourses"))
        

    except Exception as e:
        logger.exception("Unexpected error removing course-instrucotr assignment %s", courseInstructorId)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

        flash("An unexpected error occurred", "danger")
        return redirect(url_for("course.listCourses"))


@courseInstructorBp.route(
    "/instructor/courses",
    methods=["GET"]
)
@roleRequired("instructor")
def listInstructorCourses():

    try:

        instructorId = int(getCurrentUserIdentity())

        assignments = (
            courseInstructorService
            .getCoursesByInstructorId(instructorId)
        )

        courses = [
            assignment.course
            for assignment in assignments
        ]

        if wantsJson():

            return jsonify({
                "success": True,
                "courses": [
                    course.toDict()
                    for course in courses
                ]
            })

        """ return render_template(
            "course/instructorCourses.html",
            courses=courses
        ) """

        return render_template(
            "course/instructorCourses.html",
            assignments=assignments
        )



    except Exception as e:

        logger.exception(
            "Unexpected error fetching courses for instructor"
        )

        if wantsJson():

            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

        flash(
            "Unable to load your courses",
            "danger"
        )

        return redirect(
            url_for("instructor.dashboard")
        )