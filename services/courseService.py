import logging

from dao.courseDao import CourseDao
from models.course import Course
logger = logging.getLogger(__name__)


class CourseService:
    def __init__(self, courseDao):
        self.courseDao = courseDao

    def createCourse(self, courseName, description=None):
        if self.courseDao.courseExistsByName(courseName):
            raise ValueError("A course with this name already exists")

        course = Course(
            course_name=courseName,
            description=description
        )

        return self.courseDao.saveCourse(course)


    def getCourseById(self, courseId):
        course =self.courseDao.getCourseById(courseId)
        if not course:
            raise ValueError("Course not found")
        return course



    def getAllCourses(self):
        return self.courseDao.getAllCourses()

    def updateCourse(self, courseId, courseName=None, description=None):
        course = self.getCourseById(courseId)

        #if not course.name.strip() 

        if courseName and courseName != course.course_name:
            if self.courseDao.courseExistsByName(courseName):
                raise ValueError("A course with this name already exists")

            course.course_name = courseName


        if description is not None:
            course.description = description

        return self.courseDao.saveCourse(course)

    def deleteCourse(self, courseId):
        course = self.getCourseById(courseId)
        self.courseDao.deleteCourse(course)


        


        

        