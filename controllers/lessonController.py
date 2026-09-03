import logging
from flask import(
    Blueprint,  render_template,
    redirect,
    url_for,
    session,jsonify,
    request,
    flash
)

from dao.enrollmentDao import EnrollmentDao
from dao.lessonProgressDao import LessonProgressDao
from dao.moduleDao import ModuleDao
from forms.lessonForms import LessonForm, LessonUpdateForm
from dao.lessonDao import LessonDao
from services.lessonProgressService import LessonProgressService
from services.lessonService import LessonService
from config.auth import roleRequired, wantsJson, loginRequired

logger = logging.getLogger(__name__)
lessonBp = Blueprint("lesson", __name__)
lessonDao = LessonDao()
enrollmentDao = EnrollmentDao()
lessonProgressDao = LessonProgressDao()
moduleDao = ModuleDao()
lessonService = LessonService(lessonDao=lessonDao, enrollmentDao=enrollmentDao, moduleDao=moduleDao)
lessonProgressService = LessonProgressService(lessonProgressDao=lessonProgressDao, enrollmentDao=enrollmentDao)


@lessonBp.route("/modules/<int:moduleId>/lessons", methods=["GET"])
@loginRequired
def listLessons(moduleId):
    lessons = lessonService.getLessonByModuleId(moduleId)

    if wantsJson():
        return jsonify({
            "success": True,
            "lessons": [lesson.toDict() for lesson in lessons]
        })

    return render_template("lesson/lessonList.html", lessons=lessons, moduleId=moduleId)



@lessonBp.route("/lessons/<int:lessonId>", methods=["GET"])
@loginRequired
def getLesson(lessonId):
    try:
        lesson = lessonService.getLessonById(lessonId)

        if wantsJson():
            return jsonify({"success": True, "lesson": lesson.toDict()})
        return render_template("lesson/lesson.html", lesson=lesson)

    except ValueError as ve:
        logger.warning("Lesson lookup failed for id %s", lessonId)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(ve)
            }), 404

        return redirect(url_for("course.listCourses"))


    except Exception as e:
        logger.exception("Unexpected error fetching lesson %s", lessonId)
        if wantsJson():
            return jsonify({"success": False, "message": str(e)}), 400

        flash("An unexpected error occurred", "danger")
        return redirect(url_for("course.listCourses"))



@lessonBp.route("/modules/<int:moduleId>/lessons/create", methods=["GET", "POST"])
@roleRequired("admin")
def createLesson(moduleId):
    form = LessonForm()
    if form.validate_on_submit():
        try:
            lesson = lessonService.createLesson(
                moduleId,
                lessonName=form.lessonName.data,
                content=form.content.data
            )
            logger.info("Lesson created successfully: %s", lesson.lesson_name)

            if wantsJson():
                return jsonify({
                    "success": True,
                    "message": "Lesson created successfully",
                    "lesson": lesson.toDict()
                }), 201

            flash("Lesson created successfully", "success")

            return redirect(url_for("lesson.listLessons", moduleId=moduleId))


        except ValueError as ve:
            logger.warning("Lesson creation validation failed")
            if wantsJson():
                return jsonify({
                    "success": False,
                    "message" : str(ve)
                }), 400

            flash(str(ve), "danger")

        except Exception as e:
            logger.exception("Unexpected error during lesson creation")
            if wantsJson():
                return jsonify({
                    "success": False,
                    "message": str(e)
                }), 400
            flash("An unexpected error occurred", "danger")

    if request.method == "POST" and wantsJson():
        return jsonify({
            "success": False,
            "errors": form.errors
        }), 400

    return render_template("lesson/lessonForm.html", form=form, moduleId=moduleId)


@lessonBp.route("/lessons/<int:lessonId>/update", methods=["GET", "POST"])
@roleRequired("admin")
def updateLesson(lessonId):
    form = LessonUpdateForm()

   
    try:
        existingLesson = lessonService.getLessonById(lessonId)
        moduleId = existingLesson.module_id
        if request.method == "GET":
            form.lessonName.data = getattr(
                existingLesson,
                "lessonName",
                getattr(existingLesson, "lesson_name", "")
            )

            form.content.data  = existingLesson.content

        if form.validate_on_submit():
        
            lesson = lessonService.updateLesson(
                lessonId,
                lessonName=form.lessonName.data,
                content=form.content.data
            )
            logger.info("Lesson updated successfully: %s", lesson.lesson_name)

            if wantsJson():
                return jsonify({
                    "success": True,
                    "message": "Lesson updated successfully",
                    "lesson": lesson.toDict()
                })

            flash("Lesson updated successfully", "success")
            return redirect(url_for("lesson.getLesson", lessonId=lesson.id))

        if request.method == "POST" and wantsJson():
            return jsonify({
                "success": False,
                "errors": form.errors
            }), 400

        return render_template(
            "lesson/lessonForm.html",

            form=form,
            moduleId=moduleId
        )

    except ValueError as ve:
        logger.warning("Lesson update validation failed for id %s", lessonId)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(ve)
            }), 400

        flash(str(ve), "danger")
        return redirect(url_for("course.listCourses"))

    except Exception as e:
        logger.warning("Unexpected error occurred during lesson update for %s", lessonId)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

        flash("An unexpected error occurred during update", "danger")


        return redirect(url_for("course.listCourses"))

@lessonBp.route("/lessons/<int:lessonId>/delete", methods=["POST"])
@roleRequired("admin")
def deleteLesson(lessonId):
    try:
        lesson = lessonService.getLessonById(lessonId)
        moduleId = lesson.module_id
        lessonService.deleteLesson(lessonId)
        logger.info("Lesson deleted successfully: %s", lessonId)

        if wantsJson():
            return jsonify({
                "success": True,
                "message": "Lesson  deleted successfully"
            })

        flash("Lesson deleted successfully", "success")
        return redirect(url_for("lesson.listLessons", moduleId=moduleId))


    except ValueError as ve:
        logger.warning("Lesson deletion failed for id %s: error: %s", lessonId, str(ve))
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(ve)
            }), 404



        flash(str(ve), "danger")

    except Exception as e:
        logger.exception("Unexpected error during lesson deletion for id: %s with error: %s ", lessonId, str(e))
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400
        



        flash("An unexpected error occurred when trying to delete", "danger")

    return redirect(url_for("course.listCourses"))




        
@lessonBp.route(
    "/enrollments/<int:enrollmentId>/lessons/<int:lessonId>",
    methods=["GET"]
)
@roleRequired("student")
def getEnrolledLesson(enrollmentId, lessonId):

    try:
        lesson = lessonService.getLessonByEnrollment(
            enrollmentId,
            lessonId
        )

        progress = lessonProgressService.getProgressForLesson(
            enrollmentId,
            lessonId
        )

        if wantsJson():
            return jsonify({
                "success": True,
                "lesson": lesson.toDict(),
                "progress": progress.toDict() if progress else None
            })

        return render_template(
            "lesson/lesson.html",
            lesson=lesson,
            enrollmentId=enrollmentId,
            progress=progress
        )

    except ValueError as ve:
        logger.warning(
            "Lesson %s cannot be accessed through enrollment %s: %s",
            lessonId,
            enrollmentId,
            str(ve)
        )
         
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(ve)
            }), 404

        flash(str(ve), "danger")

        return redirect(
            url_for("enrollment.listMyEnrollments")
        )

    except Exception:
        logger.exception(
            "Error loading lesson %s for enrollment %s",
            lessonId,
            enrollmentId
        )

        if wantsJson():
            return jsonify({
                "success": False,
                "message": "Could not load lesson"
            }), 400

        flash("Could not load lesson", "danger")

        return redirect(
            url_for("enrollment.listMyEnrollments")
        )


@lessonBp.route(
    "/enrollments/<int:enrollmentId>/modules/<int:moduleId>/lessons",
    methods=["GET"]
)
@roleRequired("student")
def listEnrolledLessons(enrollmentId, moduleId):

    try:
        lessons = lessonService.getLessonsByEnrollmentAndModule(
            enrollmentId,
            moduleId
        )

        if wantsJson():
            return jsonify({
                "success": True,
                "lessons": [
                    lesson.toDict()
                    for lesson in lessons
                ]
            })

        return render_template(
            "lesson/lessonList.html",
            lessons=lessons,
            moduleId=moduleId,
            enrollmentId=enrollmentId
        )

    except ValueError as ve:

        logger.warning(
            "Could not load lessons for enrollment %s, module %s: %s",
            enrollmentId,
            moduleId,
            str(ve)
        )

        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(ve)
            }), 404

        flash(str(ve), "danger")

        return redirect(
            url_for("enrollment.listMyEnrollments")
        )

    except Exception:

        logger.exception(
            "Unexpected error loading lessons"
        )

        if wantsJson():
            return jsonify({
                "success": False,
                "message": "Could not load lessons"
            }), 400

        flash("Could not load lessons", "danger")

        return redirect(
            url_for("enrollment.listMyEnrollments")
        )