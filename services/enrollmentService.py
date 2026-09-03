import logging

from models.enrollment import Enrollment
from config.auth import wantsJson, loginRequired, roleRequired, getCurrentUserIdentity

logger = logging.getLogger(__name__)

class EnrollmentService:

    def __init__(self, enrollmentDao, courseInstructorDao):
        self.enrollmentDao = enrollmentDao
        self.courseInstructorDao = courseInstructorDao


    def enrollStudent(self, studentId, courseInstructorId):
        courseInstructor = self.courseInstructorDao.getCourseInstructorById(courseInstructorId)

        if not courseInstructor:
            raise ValueError("Course Offering Not found")

        if self.enrollmentDao.enrollmentExists(studentId, courseInstructorId):
            raise ValueError("Student is already enrolled in this course")


        enrollment = Enrollment(
            student_id=studentId,
            course_instructor_id=courseInstructorId,
            status="not_started"
        )

        return self.enrollmentDao.saveEnrollment(enrollment)


    def getEnrolledById(self, enrollmentId):
        enrollment = self.enrollmentDao.getEnrollmentById(enrollmentId)

        if not enrollment:
            raise ValueError("Enrollment not found")
        return enrollment


    def getEnrollmentsByStudentId(self, studentId):
        return self.enrollmentDao.getEnrollmentByStudentId(studentId)

    def getEnrollmentByCourseInstructorId(self, courseInstructorId, userId, role):
        courseInstructor = self.courseInstructorDao.getCourseInstructorById(courseInstructorId)
        if not courseInstructor:
            raise ValueError("Course instructor offering not found")

        if role != "admin" and courseInstructor.instructor_id != int(userId):
            raise PermissionError("You are not authoried to view enrollments for this offering")

       
        return self.enrollmentDao.getEnrollmentsByCourseInstructorId(courseInstructorId)


    def updateStatus(self, enrollmentId, status):
        allowedStatuses = ("not_started", "ongoing", "completed")
        if status not in allowedStatuses:
            raise ValueError("Invalid status value")

        enrollment = self.getEnrolledById(enrollmentId)

        enrollment.status = status
        return self.enrollmentDao.saveEnrollment(enrollment)


    def unenrollStudent(self, enrollmentId, studentId):
        enrollment = self.getEnrolledById(enrollmentId)
        if enrollment.student_id != studentId:
            raise PermissionError(
                "You are not autthorize to unenroll this student"
            )
        self.enrollmentDao.deleteEnrollment(enrollment)