import logging

from models.quiz import Quiz
from models.question import Question
from models.quizRecord import QuizRecord

logger = logging.getLogger(__name__)


class QuizService:
    def __init__(self, quizDao, questionDao, quizRecordDao,
                 courseInstructorDao, enrollmentDao):
        self.quizDao = quizDao
        self.questionDao = questionDao
        self.quizRecordDao = quizRecordDao
        self.courseInstructorDao = courseInstructorDao
        self.enrollmentDao = enrollmentDao

    # ---------- internal helpers ----------

    def _getCourseInstructorOrRaise(self, courseInstructorId):
        courseInstructor = self.courseInstructorDao.getCourseInstructorById(courseInstructorId)
        if not courseInstructor:
            raise ValueError("Course instructor assignment not found")
        return courseInstructor

    def _assertTeaches(self, courseInstructor, instructorId):
        if courseInstructor is None or courseInstructor.instructor_id != instructorId:
            raise PermissionError("You do not teach this course")

    def _getQuizOrRaise(self, quizId):
        quiz = self.quizDao.getQuizById(quizId)
        if not quiz:
            raise ValueError("Quiz not found")
        return quiz

    # ---------- quiz management (instructor) ----------

    def createQuiz(self, instructorId, courseInstructorId, quizName, description=None):
        courseInstructor = self._getCourseInstructorOrRaise(courseInstructorId)
        self._assertTeaches(courseInstructor, instructorId)

        if self.quizDao.quizExistsByName(courseInstructorId, quizName):
            raise ValueError("A quiz with this name already exists for this course")

        quiz = Quiz(
            course_instructor_id=courseInstructorId,
            instructor_id=instructorId,
            quiz_name=quizName,
            description=description
        )
        return self.quizDao.saveQuiz(quiz)

    def getQuizById(self, quizId):
        return self._getQuizOrRaise(quizId)

    def getQuizzesForCourseInstructor(self, courseInstructorId):
        self._getCourseInstructorOrRaise(courseInstructorId)
        return self.quizDao.getQuizzesByCourseInstructor(courseInstructorId)

    def getQuizzesForInstructor(self, instructorId):
        return self.quizDao.getQuizzesByInstructor(instructorId)

    def deleteQuiz(self, quizId, instructorId):
        quiz = self._getQuizOrRaise(quizId)
        self._assertTeaches(quiz.course_instructor, instructorId)
        self.quizDao.deleteQuiz(quiz)

    # ---------- question management (instructor) ----------

    def addQuestion(self, quizId, instructorId, questionText, options, correctOption, points=1):
        quiz = self._getQuizOrRaise(quizId)
        self._assertTeaches(quiz.course_instructor, instructorId)

        cleanedOptions = [opt.strip() for opt in options if opt and opt.strip()]
        if len(cleanedOptions) < 2:
            raise ValueError("A question needs at least two options")

        if len(set(cleanedOptions)) != len(cleanedOptions):
            raise ValueError("Options must be unique")

        if not correctOption or correctOption.strip() not in cleanedOptions:
            raise ValueError("Correct option must match one of the provided options")

        correctOption = correctOption.strip()
        questionOptions = {opt: (opt == correctOption) for opt in cleanedOptions}

        question = Question(
            quiz_id=quizId,
            question_text=questionText,
            question_options=questionOptions,
            points=points or 1
        )
        return self.questionDao.saveQuestion(question)

    def getQuestionsForQuiz(self, quizId):
        self._getQuizOrRaise(quizId)
        return self.questionDao.getQuestionsByQuiz(quizId)

    def deleteQuestion(self, quizId, questionId, instructorId):
        quiz = self._getQuizOrRaise(quizId)
        self._assertTeaches(quiz.course_instructor, instructorId)

        question = self.questionDao.getQuestionById(questionId)
        if not question or question.quiz_id != quizId:
            raise ValueError("Question not found for this quiz")

        self.questionDao.deleteQuestion(question)

    # ---------- taking the quiz (student) ----------

    def getQuizForStudent(self, quizId, studentId):
        quiz = self._getQuizOrRaise(quizId)

        if not self.enrollmentDao.enrollmentExists(studentId, quiz.course_instructor_id):
            raise PermissionError("You are not enrolled in this course")

        existingRecord = self.quizRecordDao.getRecordByQuizAndStudent(quizId, studentId)
        return quiz, existingRecord

    def submitQuiz(self, quizId, studentId, answers):
        quiz = self._getQuizOrRaise(quizId)

        if not self.enrollmentDao.enrollmentExists(studentId, quiz.course_instructor_id):
            raise PermissionError("You are not enrolled in this course")

        if self.quizRecordDao.getRecordByQuizAndStudent(quizId, studentId):
            raise ValueError("You have already taken this quiz")

        questions = self.questionDao.getQuestionsByQuiz(quizId)
        if not questions:
            raise ValueError("This quiz has no questions yet")

        score = 0
        for question in questions:
            selected = answers.get(str(question.id))
            if selected and question.question_options.get(selected) is True:
                score += question.points

        record = QuizRecord(
            quiz_id=quizId,
            student_id=studentId,
            score=score,
            quiz_answer=answers
        )
        return self.quizRecordDao.saveRecord(record)

    # ---------- records ----------

    def getRecordsForQuiz(self, quizId, instructorId):
        quiz = self._getQuizOrRaise(quizId)
        self._assertTeaches(quiz.course_instructor, instructorId)
        return self.quizRecordDao.getRecordsByQuiz(quizId)

    def getStudentRecord(self, quizId, studentId):
        return self.quizRecordDao.getRecordByQuizAndStudent(quizId, studentId)

    def getRecordsForStudent(self, studentId):
        return self.quizRecordDao.getRecordsByStudent(studentId)

    # ---------- serialization ----------

    @staticmethod
    def toQuizDict(quiz):
        return {
            "id": quiz.id,
            "course_instructor_id": quiz.course_instructor_id,
            "instructor_id": quiz.instructor_id,
            "quiz_name": quiz.quiz_name,
            "description": quiz.description,
            "created_at": quiz.created_at.isoformat() if quiz.created_at else None,
            "updated_at": quiz.updated_at.isoformat() if quiz.updated_at else None
        }

    @staticmethod
    def toQuestionDict(question, includeAnswer=False):
        data = {
            "id": question.id,
            "quiz_id": question.quiz_id,
            "question_text": question.question_text,
            "options": list(question.question_options.keys()),
            "points": question.points
        }
        if includeAnswer:
            data["correct_option"] = next(
                (opt for opt, isCorrect in question.question_options.items() if isCorrect),
                None
            )
        return data

    @staticmethod
    def toRecordDict(record):
        return {
            "id": record.id,
            "quiz_id": record.quiz_id,
            "student_id": record.student_id,
            "score": record.score,
            "quiz_answer": record.quiz_answer,
            "created_at": record.created_at.isoformat() if record.created_at else None
        }