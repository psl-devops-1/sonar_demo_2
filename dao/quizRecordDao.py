from config.database import db
from models.quizRecord import QuizRecord


class QuizRecordDao:
    def getRecordById(self, recordId):
        return db.session.get(QuizRecord, recordId)

    def getRecordByQuizAndStudent(self, quizId, studentId):
        return QuizRecord.query.filter_by(
            quiz_id=quizId,
            student_id=studentId
        ).first()

    def getRecordsByQuiz(self, quizId):
        return QuizRecord.query.filter_by(
            quiz_id=quizId
        ).order_by(QuizRecord.id).all()

    def getRecordsByStudent(self, studentId):
        return QuizRecord.query.filter_by(
            student_id=studentId
        ).order_by(QuizRecord.id).all()

    def saveRecord(self, record):
        db.session.add(record)
        db.session.commit()
        return record