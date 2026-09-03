from config.database import db
from models.quiz import Quiz


class QuizDao:
    def getQuizById(self, quizId):
        return db.session.get(Quiz, quizId)

    def getQuizzesByCourseInstructor(self, courseInstructorId):
        return Quiz.query.filter_by(
            course_instructor_id=courseInstructorId
        ).order_by(Quiz.id).all()

    def getQuizzesByInstructor(self, instructorId):
        return Quiz.query.filter_by(
            instructor_id=instructorId
        ).order_by(Quiz.id).all()

    def saveQuiz(self, quiz):
        db.session.add(quiz)
        db.session.commit()
        return quiz

    def deleteQuiz(self, quiz):
        db.session.delete(quiz)
        db.session.commit()

    def quizExistsByName(self, courseInstructorId, quizName):
        return Quiz.query.filter_by(
            course_instructor_id=courseInstructorId,
            quiz_name=quizName
        ).first() is not None