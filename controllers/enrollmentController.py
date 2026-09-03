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

from dao.enrollmentDao import EnrollmentDao
from dao.courseInstructorDao import CourseInstructorDao
from services.enrollmentService import EnrollmentService
from config.auth import getCurrentUserClaims, wantsJson, loginRequired, roleRequired, getCurrentUserIdentity

logger = logging.getLogger(__name__)
enrollmentBp = Blueprint("enrollment", __name__)

enrollmentDao = EnrollmentDao()
courseInstructorDao = CourseInstructorDao()
enrollmentService = EnrollmentService(enrollmentDao, courseInstructorDao)

@enrollmentBp.route("/enrollments", methods=["GET"])
@roleRequired("student")
def listMyEnrollments():
    studentId = getCurrentUserIdentity()
    enrollments = enrollmentService.getEnrollmentsByStudentId(studentId)

    if wantsJson():
        return jsonify({
            "success": True,
            "enrollments": [enrollment.toDict() for enrollment in enrollments]
        })

    return render_template(
        "enrollment/myEnrollments.html",
        enrollments=enrollments
    )



@enrollmentBp.route("/courseInstructors/<int:courseInstructorId>/enroll", methods=["POST"])
@roleRequired("student")
def enroll(courseInstructorId):
    studentId =  getCurrentUserIdentity()


    try:
        enrollment = enrollmentService.enrollStudent(studentId, courseInstructorId)
        logger.info("Student %s enrolled via course-instructor %s", studentId, courseInstructorId)

        if wantsJson():
            return jsonify({
                "success": True,
                "message": "Enrolled Successfully",
                "enrollment": enrollment.toDict()
            }), 201

        flash("Enrolled successfully", "success")
        return redirect(url_for("enrollment.listMyEnrollments"))

    
    except ValueError as ve:
        logger.warning("Enrollment failed for student %s: %s", studentId, str(ve))
        if wantsJson():
            return jsonify({"success": False, "message": str(ve)}), 400

        flash(str(ve), "danger")

        return redirect(url_for("course.listCourses"))


    except Exception as e:
        logger.exception("Unexpected error enrolling student %s", studentId)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

        flash("An unexpected error occurred", "danger")
        return redirect(url_for("course.listCourses"))


@enrollmentBp.route("/courseInstructors/<int:courseInstructorId>/enrollments", methods=["GET"])
@roleRequired("admin", "instructor")
def listEnrollmentsForOffering(courseInstructorId):
   

    try:
        userId = getCurrentUserIdentity()
        role = getCurrentUserClaims().get("role")
    
        enrollments = enrollmentService.getEnrollmentByCourseInstructorId(courseInstructorId, userId, role )
        if wantsJson():
            return jsonify({
                "success": True,
                "enrollments": [enrollment.toDict() for enrollment in enrollments]
            
            })

        return render_template(
            "enrollment/offeringEnrollments.html",
            enrollments=enrollments,
            courseInstructorId=courseInstructorId
        )
    except PermissionError as pe:
        logger.warning("Unauthorized access attempete by user on enrollments %s", pe)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(pe)
            }), 403

        flash(str(pe), "danger")
        return redirect(url_for("course.listCourses"))
    except ValueError as ve:
       
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(ve)
            }), 404

        flash(str(ve), "danger")
        return redirect(url_for("course.listCourses"))
    except Exception as e:
        logger.exception("An exception occured when trying to get enrollments for a CI with error %s", str(e))
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(e)
            }), 404

        flash("Could not get enrollments", "danger")
        return redirect(url_for("course.listCourses"))

    


@enrollmentBp.route("/enrollments/<int:enrollmentId>/unenroll", methods=["POST"])
@roleRequired("student")
def unenroll(enrollmentId):
    try:
        studentId = int(getCurrentUserIdentity())
        
        enrollmentService.unenrollStudent(enrollmentId=enrollmentId, studentId=studentId)

        logger.info("Enrollment %s removed", enrollmentId)

        if wantsJson():
            return jsonify({
                "success": True,
                "message": "Unenrolled successfully"
            })

        flash("Unenrolled successfully", "success")

    except ValueError as ve:
        logger.warning("Unenroll failed for id %s", enrollmentId)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(ve)
            }), 404

        flash(str(ve), "danger")
    except PermissionError as pe:
        logger.warning("Unenroll failed for id %s due to unauthoried permission", enrollmentId)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(ve)
            }), 404

        flash("You are not authorized to unenroll this student", "danger")
    except Exception as e:
        logger.exception("Unexpected error unenrolling %s", enrollmentId)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

        flash("An unexpected error occurred", "danger")

    return redirect(url_for("enrollment.listMyEnrollments"))




@enrollmentBp.route(
    "/enrollments/<int:enrollmentId>/learn",
    methods=["GET"]
)
@roleRequired("student")
def learning(enrollmentId):

    try:
        studentId = int(getCurrentUserIdentity())

        enrollment = enrollmentService.getEnrolledById(enrollmentId)

        if enrollment.student_id != studentId:
            raise PermissionError(
                "You are not authorized to access this enrollment"
            )

        courseInstructor = enrollment.course_instructor

        course = courseInstructor.course

        modules = course.modules

        return render_template(
            "enrollment/learning.html",
            enrollment=enrollment,
            course=course,
            courseInstructor=courseInstructor,
            modules=modules
        )

    except PermissionError as pe:

        flash(str(pe), "danger")

        return redirect(
            url_for("enrollment.listMyEnrollments")
        )

    except ValueError as ve:

        flash(str(ve), "danger")

        return redirect(
            url_for("enrollment.listMyEnrollments")
        )

    except Exception:

        logger.exception(
            "Unexpected error opening enrollment %s",
            enrollmentId
        )

        flash(
            "Could not open this course",
            "danger"
        )

        return redirect(
            url_for("enrollment.listMyEnrollments")
        )