from config.database import db
from models.course import Course


class CourseDao:
    def getCourseById(self, courseId):
        return db.session.get(Course, courseId)

    def getCourseByName(self, courseName):
        return Course.query.filter_by(
            course_name=courseName
        ).first()

    def getAllCourses(self):
        return Course.query.order_by(
            Course.id
        ).all()

    def saveCourse(self, course):
        db.session.add(course)
        db.session.commit()
        return course


    def deleteCourse(self, course):
        db.session.delete(course)
        db.session.commit()

    def courseExistsByName(self, courseName):
        return Course.query.filter_by(
            course_name=courseName
        ).first() is not None