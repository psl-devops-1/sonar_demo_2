from config.database import db
from models.enrollment import Enrollment

class EnrollmentDao:

    def getEnrollmentById(self, enrollmentId):
        return db.session.get(Enrollment, enrollmentId)

    #getEnrollment(self, studentId, courseInstructorId):
    def getByStudentAndCourseInstructor(self, studentId, courseInstructorId):
        return Enrollment.query.filter_by(
            student_id=studentId,
            course_instructor_id=courseInstructorId
        ).first()


    def getEnrollmentByStudentId(self, studentId):
        return Enrollment.query.filter_by(
            student_id=studentId
        ).order_by(Enrollment.id).all()


    def getEnrollmentsByCourseInstructorId(self, courseInstructorId):
        return Enrollment.query.filter_by(
            course_instructor_id=courseInstructorId
        ).order_by(Enrollment.id).all()


    def saveEnrollment(self, enrollment):
        db.session.add(enrollment)
        db.session.commit()
        return enrollment

    def deleteEnrollment(self, enrollment):
        db.session.delete(enrollment)
        db.session.commit()

    #isStudentEnrolled:
    def enrollmentExists(self, studentId, courseInstructorId):
        return Enrollment.query.filter_by(
            student_id=studentId,
            course_instructor_id=courseInstructorId
        ).first() is not None

    def updateStatus(self, enrollmentId, status):
        enrollment = self.getEnrollmentById(enrollmentId)
        if enrollment:
            enrollment.status = status

            db.session.commit()
            return enrollment

        return None