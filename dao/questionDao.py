from config.database import db
from models.question import Question


class QuestionDao:
    def getQuestionById(self, questionId):
        return db.session.get(Question, questionId)

    def getQuestionsByQuiz(self, quizId):
        return Question.query.filter_by(
            quiz_id=quizId
        ).order_by(Question.id).all()

    def saveQuestion(self, question):
        db.session.add(question)
        db.session.commit()
        return question

    def deleteQuestion(self, question):
        db.session.delete(question)
        db.session.commit()