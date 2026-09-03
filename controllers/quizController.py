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

from config.auth import getCurrentUserClaims, getCurrentUserIdentity

from forms.quizForms import QuizForm, QuestionForm
from dao.quizDao import QuizDao
from dao.questionDao import QuestionDao
from dao.quizRecordDao import QuizRecordDao
from dao.courseInstructorDao import CourseInstructorDao
from dao.enrollmentDao import EnrollmentDao
from services.quizService import QuizService
from config.auth import wantsJson, loginRequired, roleRequired


logger = logging.getLogger(__name__)

quizBp = Blueprint(
    "quiz",
    __name__
)


quizDao = QuizDao()
questionDao = QuestionDao()
quizRecordDao = QuizRecordDao()
courseInstructorDao = CourseInstructorDao()
enrollmentDao = EnrollmentDao()

quizService = QuizService(
    quizDao,
    questionDao,
    quizRecordDao,
    courseInstructorDao,
    enrollmentDao
)


@quizBp.route("/course-instructors/<int:courseInstructorId>/quizzes", methods=["GET"])
@loginRequired
def listQuizzes(courseInstructorId):
    try:
        quizzes = quizService.getQuizzesForCourseInstructor(courseInstructorId)

        if wantsJson():
            return jsonify({
                "success": True,
                "quizzes": [quizService.toQuizDict(q) for q in quizzes]
            })

        return render_template(
            "quiz/quizList.html",
            quizzes=quizzes,
            courseInstructorId=courseInstructorId
        )

    except ValueError as ve:
        logger.warning("Quiz list failed for course instructor %s: %s", courseInstructorId, str(ve))
        if wantsJson():
            return jsonify({"success": False, "message": str(ve)}), 404

        flash(str(ve), "danger")
        return redirect(url_for("course.listCourses"))


@quizBp.route("/course-instructors/<int:courseInstructorId>/quizzes/create", methods=["GET", "POST"])
@roleRequired("instructor")
def createQuiz(courseInstructorId):
    form = QuizForm()

    if form.validate_on_submit():
        try:
            currentUserId = int(getCurrentUserIdentity())
            quiz = quizService.createQuiz(
                instructorId=currentUserId,
                courseInstructorId=courseInstructorId,
                quizName=form.quizName.data,
                description=form.description.data
            )
            logger.info("Quiz created successfully: %s", quiz.quiz_name)

            if wantsJson():
                return jsonify({
                    "success": True,
                    "message": "Quiz created successfully",
                    "quiz": quizService.toQuizDict(quiz)
                }), 201

            flash("Quiz created successfully", "success")
            return redirect(url_for("quiz.getQuiz", quizId=quiz.id))

        except PermissionError as pe:
            logger.warning("Unauthorized quiz creation attempt: %s", str(pe))
            if wantsJson():
                return jsonify({"success": False, "message": str(pe)}), 403
            flash(str(pe), "danger")

        except ValueError as ve:
            logger.warning("Quiz creation validation failed: %s", str(ve))
            if wantsJson():
                return jsonify({"success": False, "message": str(ve)}), 400
            flash(str(ve), "danger")

        except Exception as e:
            logger.exception("Unexpected error during quiz creation")
            if wantsJson():
                return jsonify({"success": False, "message": str(e)}), 400
            flash("An unexpected error occurred", "danger")

    if request.method == "POST" and wantsJson():
        logger.warning("Form validation failed on quiz creation: %s", form.errors)
        return jsonify({"success": False, "errors": form.errors}), 400

    return render_template(
        "quiz/quizForm.html",
        form=form,
        courseInstructorId=courseInstructorId
    )


@quizBp.route("/quizzes/<int:quizId>", methods=["GET"])
@loginRequired
def getQuiz(quizId):
    try:
        quiz = quizService.getQuizById(quizId)
        questions = quizService.getQuestionsForQuiz(quizId)
        currentUserId = int(getCurrentUserIdentity())
        currentUserRole =  getCurrentUserClaims().get("role")

        isOwner = (
            currentUserRole == "instructor"
            and quiz.instructor_id == currentUserId
        )

        if wantsJson():
            return jsonify({
                "success": True,
                "quiz": quizService.toQuizDict(quiz),
                "questions": [
                    quizService.toQuestionDict(q, includeAnswer=isOwner)
                    for q in questions
                ]
            })

        if currentUserRole == "student" and not isOwner:
            return redirect(url_for("quiz.takeQuiz", quizId=quizId))

        return render_template(
            "quiz/quizDetail.html",
            quiz=quiz,
            questions=questions,
            isOwner=isOwner
        )

    except ValueError as ve:
        logger.warning("Quiz lookup failed for id %s: %s", quizId, str(ve))
        if wantsJson():
            return jsonify({"success": False, "message": str(ve)}), 404

        flash(str(ve), "danger")
        return redirect(url_for("course.listCourses"))

    except Exception as e:
        logger.exception("Unexpected error fetching quiz %s", quizId)
        if wantsJson():
            return jsonify({"success": False, "message": str(e)}), 400

        flash("An unexpected error occurred", "danger")
        return redirect(url_for("course.listCourses"))


@quizBp.route("/quizzes/<int:quizId>/questions/create", methods=["GET", "POST"])
@roleRequired("instructor")
def addQuestion(quizId):
    form = QuestionForm()


    if form.validate_on_submit():
        try:
            optionsMap = {
                "option1": form.option1.data,
                "option2": form.option2.data,
                "option3": form.option3.data,
                "option4": form.option4.data
            }
            correctOptionText = optionsMap.get(form.correctOption.data)
            currentUserId = int(getCurrentUserIdentity())
            

            quizService.addQuestion(
                quizId=quizId,
                instructorId=currentUserId,
                questionText=form.questionText.data,
                options=list(optionsMap.values()),
                correctOption=correctOptionText,
                points=form.points.data
            )
            logger.info("Question added to quiz %s", quizId)

            if wantsJson():
                return jsonify({
                    "success": True,
                    "message": "Question added successfully"
                }), 201

            flash("Question added successfully", "success")
            return redirect(url_for("quiz.getQuiz", quizId=quizId))

        except PermissionError as pe:
            logger.warning("Unauthorized question add attempt: %s", str(pe))
            if wantsJson():
                return jsonify({"success": False, "message": str(pe)}), 403
            flash(str(pe), "danger")

        except ValueError as ve:
            logger.warning("Question validation failed for quiz %s: %s", quizId, str(ve))
            if wantsJson():
                return jsonify({"success": False, "message": str(ve)}), 400
            flash(str(ve), "danger")

        except Exception as e:
            logger.exception("Unexpected error adding question to quiz %s", quizId)
            if wantsJson():
                return jsonify({"success": False, "message": str(e)}), 400
            flash("An unexpected error occurred", "danger")

    if request.method == "POST" and wantsJson():
        logger.warning("Form validation failed on question creation: %s", form.errors)
        return jsonify({"success": False, "errors": form.errors}), 400

    return render_template(
        "quiz/questionForm.html",
        form=form,
        quizId=quizId
    )


@quizBp.route("/quizzes/<int:quizId>/questions/<int:questionId>/delete", methods=["POST"])
@roleRequired("instructor")
def deleteQuestion(quizId, questionId):
    try:
        currentUserId = int(getCurrentUserIdentity())
        #currentUserRole =  getCurrentUserClaims().get("role")
        quizService.deleteQuestion(quizId, questionId, currentUserId)
        logger.info("Question %s deleted from quiz %s", questionId, quizId)

        if wantsJson():
            return jsonify({"success": True, "message": "Question deleted successfully"})

        flash("Question deleted successfully", "success")

    except PermissionError as pe:
        if wantsJson():
            return jsonify({"success": False, "message": str(pe)}), 403
        flash(str(pe), "danger")

    except ValueError as ve:
        if wantsJson():
            return jsonify({"success": False, "message": str(ve)}), 404
        flash(str(ve), "danger")

    except Exception as e:
        logger.exception("Unexpected error deleting question %s", questionId)
        if wantsJson():
            return jsonify({"success": False, "message": str(e)}), 400
        flash("An unexpected error occurred", "danger")

    return redirect(url_for("quiz.getQuiz", quizId=quizId))


@quizBp.route("/quizzes/<int:quizId>/take", methods=["GET", "POST"])
@loginRequired
def takeQuiz(quizId):
    try:
        if request.method == "GET":
            currentUserId = int(getCurrentUserIdentity())
            currentUserRole =  getCurrentUserClaims().get("role")
            quiz, existingRecord = quizService.getQuizForStudent(quizId, currentUserId)

            if existingRecord:
                return redirect(url_for("quiz.quizResult", quizId=quizId))

            questions = quizService.getQuestionsForQuiz(quizId)

            if wantsJson():
                return jsonify({
                    "success": True,
                    "quiz": quizService.toQuizDict(quiz),
                    "questions": [
                        quizService.toQuestionDict(q, includeAnswer=False)
                        for q in questions
                    ]
                })

            return render_template(
                "quiz/quizTake.html",
                quiz=quiz,
                questions=questions
            )

        answers = {}
        for key, value in request.form.items():
            if key.startswith("question_"):
                questionId = key.replace("question_", "")
                answers[questionId] = value

        currentUserId = int(getCurrentUserIdentity())
        currentUserRole =  getCurrentUserClaims().get("role")

        record = quizService.submitQuiz(quizId, currentUserId, answers)
        logger.info("Student %s submitted quiz %s, score %s", currentUserId, quizId, record.score)

        if wantsJson():
            return jsonify({
                "success": True,
                "message": "Quiz submitted successfully",
                "record": quizService.toRecordDict(record)
            }), 201

        flash("Quiz submitted successfully", "success")
        return redirect(url_for("quiz.quizResult", quizId=quizId))

    except PermissionError as pe:
        logger.warning("Unauthorized quiz attempt: %s", str(pe))
        if wantsJson():
            return jsonify({"success": False, "message": str(pe)}), 403
        flash(str(pe), "danger")
        return redirect(url_for("course.listCourses"))

    except ValueError as ve:
        logger.warning("Quiz submission failed for quiz %s: %s", quizId, str(ve))
        if wantsJson():
            return jsonify({"success": False, "message": str(ve)}), 400
        flash(str(ve), "danger")
        return redirect(url_for("quiz.getQuiz", quizId=quizId))

    except Exception as e:
        logger.exception("Unexpected error during quiz attempt for quiz %s", quizId)
        if wantsJson():
            return jsonify({"success": False, "message": str(e)}), 400
        flash("An unexpected error occurred", "danger")
        return redirect(url_for("course.listCourses"))


@quizBp.route("/quizzes/<int:quizId>/result", methods=["GET"])
@loginRequired
def quizResult(quizId):
    try:
        currentUserId = int(getCurrentUserIdentity())
        #currentUserRole =  getCurrentUserClaims().get("role")       
        record = quizService.getStudentRecord(quizId, currentUserId)
        if not record:
            flash("You have not taken this quiz yet", "warning")
            return redirect(url_for("quiz.takeQuiz", quizId=quizId))

        quiz = quizService.getQuizById(quizId)
        questions = quizService.getQuestionsForQuiz(quizId)

        if wantsJson():
            return jsonify({
                "success": True,
                "record": quizService.toRecordDict(record)
            })

        return render_template(
            "quiz/quizResult.html",
            quiz=quiz,
            record=record,
            questions=questions
        )

    except ValueError as ve:
        if wantsJson():
            return jsonify({"success": False, "message": str(ve)}), 404
        flash(str(ve), "danger")
        return redirect(url_for("course.listCourses"))


@quizBp.route("/quizzes/<int:quizId>/records", methods=["GET"])
@roleRequired("instructor")
def quizRecords(quizId):
    try:
        currentUserId = int(getCurrentUserIdentity())
        #currentUserRole =  getCurrentUserClaims().get("role")
        quiz = quizService.getQuizById(quizId)
        records = quizService.getRecordsForQuiz(quizId, currentUserId)

        if wantsJson():
            return jsonify({
                "success": True,
                "records": [quizService.toRecordDict(r) for r in records]
            })

        return render_template(
            "quiz/quizRecords.html",
            quiz=quiz,
            records=records
        )

    except PermissionError as pe:
        if wantsJson():
            return jsonify({"success": False, "message": str(pe)}), 403
        flash(str(pe), "danger")
        return redirect(url_for("course.listCourses"))

    except ValueError as ve:
        if wantsJson():
            return jsonify({"success": False, "message": str(ve)}), 404
        flash(str(ve), "danger")
        return redirect(url_for("course.listCourses"))


@quizBp.route("/quizzes/<int:quizId>/delete", methods=["POST"])
@roleRequired("instructor")
def deleteQuiz(quizId):
    try:
        currentUserId = int(getCurrentUserIdentity())
        #currentUserRole =  getCurrentUserClaims().get("role")
        quizService.deleteQuiz(quizId, currentUserId)
        logger.info("Quiz deleted successfully: %s", quizId)

        if wantsJson():
            return jsonify({"success": True, "message": "Quiz deleted successfully"})

        flash("Quiz deleted successfully", "success")

    except PermissionError as pe:
        if wantsJson():
            return jsonify({"success": False, "message": str(pe)}), 403
        flash(str(pe), "danger")

    except ValueError as ve:
        if wantsJson():
            return jsonify({"success": False, "message": str(ve)}), 404
        flash(str(ve), "danger")

    except Exception as e:
        logger.exception("Unexpected error during quiz deletion for id %s", quizId)
        if wantsJson():
            return jsonify({"success": False, "message": str(e)}), 400
        flash("An unexpected error occurred", "danger")

    return redirect(url_for("course.listCourses"))