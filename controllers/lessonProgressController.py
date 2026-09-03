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

from dao.enrollmentDao import EnrollmentDao
from dao.lessonProgressDao import LessonProgressDao
from services.lessonProgressService import LessonProgressService
from config.auth import getCurrentUserIdentity, wantsJson, loginRequired, roleRequired


logger = logging.getLogger(__name__)

lessonProgressBp = Blueprint("lessonProgress", __name__)
lessonProgressDao = LessonProgressDao()
enrollmentDao = EnrollmentDao()
lessonProgressService = LessonProgressService(lessonProgressDao=lessonProgressDao, enrollmentDao=enrollmentDao)

@lessonProgressBp.route("/enrollments/<int:enrollmentId>/progress", methods=["GET"])
@roleRequired("student", "instructor", "admin")
def getProgress(enrollmentId):
    try:
        records = lessonProgressService.getProgressByEnrollmentId(enrollmentId)

        if wantsJson():
            return jsonify({
                "success": True,
                "progress": [record.toDict() for record in records]
            })

        return render_template(
            "lessonProgress/progress.html",
            enrollmentId=enrollmentId,
            records=records
        )

    except Exception as e:
        logger.exception("Unexpected error fetching progress for enrollment %s", enrollmentId)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

        flash("An unexpected error occurred", "danger")
        return redirect(url_for("course.listCourses"))


@lessonProgressBp.route(
    "/enrollments/<int:enrollmentId>/lessons/<int:lessonId>/complete",
    methods=["POST"]
)
@roleRequired("student")
def markLessonComplete(enrollmentId, lessonId):
    try:
        if request.is_json:
            data = request.get_json(silent=True) or {}
            completed = data.get("completed", True)
        else:
            completed = request.form.get("completed", "true").lower() == "true"

        enrollment = enrollmentDao.getEnrollmentById(enrollmentId)
        userId = int(getCurrentUserIdentity())
        progress = lessonProgressService.markLessonComplete(
            enrollmentId,
            lessonId,
            completed=completed
        )

        logger.info(
            "Lesson progress updated: enrollment=%s lesson=%s completed=%s",
            enrollmentId, lessonId, progress.completed
                            )

        if wantsJson():
            return jsonify({
                "success": True,
                "message": "Progress updated",
                "progress": progress.toDict()
            })

        flash("Lesson marked as completed", "success")
        return redirect(
            url_for(
                "lesson.getEnrolledLesson",
                enrollmentId=enrollmentId,
                lessonId=lessonId
            )
        )

    except ValueError as ve:
        logger.warning(
                    "Progress update failed for enrollment %s lesson %s",
                    enrollmentId,
                    lessonId
                )

        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(ve)
            }), 400

        flash(str(ve), "danger")

        return redirect(
            url_for(
                "lesson.getEnrolledLesson",
                enrollmentId=enrollmentId,
                lessonId=lessonId
            )
        )
    except PermissionError as pe:
        logger.warning("Progress update attempted  for enrollment %s lesson %s by unauthorized user",
                        enrollmentId, lessonId)

        if wantsJson():

            return jsonify({
                "success": False,
                "message": str(pe)
            }), 400

        flash("You are not authorized to complete this lesson", "danger")
        
        return redirect(
            url_for(
                "lesson.getEnrolledLesson",
                enrollmentId=enrollmentId,
                lessonId=lessonId
            )
        )
        

    except Exception as e:
        logger.exception(
            "Progress update failed for enrollment %s lesson %s",
            enrollmentId,
            lessonId
        )

        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

        flash(
            "Could not update lesson progress",
            "danger"
        )

        return redirect(
            url_for(
                "lesson.getEnrolledLesson",
                enrollmentId=enrollmentId,
                lessonId=lessonId
            )
        )
