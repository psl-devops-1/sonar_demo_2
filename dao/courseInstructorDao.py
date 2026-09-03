from config.database import db
from models.courseInstructor import CourseInstructor


class CourseInstructorDao:

    def getCourseInstructorById(self, courseInstructorId):
        return db.session.get(CourseInstructor, courseInstructorId)


    def getByCourseAndInstructor(self, courseId, instructorId):
        return CourseInstructor.query.filter_by(
            course_id=courseId,
            instructor_id=instructorId
        ).first()

    #   getCourseInstructorsByCourse(self, courseId):
    def getInstructorsByCourseId(self, courseId):
        return CourseInstructor.query.filter_by(
            course_id=courseId
        ).order_by(CourseInstructor.id).all()


    #   getCourseInstructorsByInstructor(self, instructorId):
    def getCoursesByInstructorId(self, instructorId):
        return CourseInstructor.query.filter_by(
            instructor_id=instructorId
        ).order_by(CourseInstructor.id).all()


    def saveCourseInstructor(self, courseInstructor):
        db.session.add(courseInstructor)
        db.session.commit()
        return courseInstructor


    def deleteCourseInstructor(self, courseInstructor):
        db.session.delete(courseInstructor)
        db.session.commit()


    def courseInstructorExists(self, courseId, instructorId):
        return CourseInstructor.query.filter_by(
            course_id=courseId,
            instructor_id=instructorId
        ).first() is not None