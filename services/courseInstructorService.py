import logging

from models.courseInstructor import CourseInstructor
logger = logging.getLogger(__name__)


class CourseInstructorService:

    def __init__(self, courseInstructorDao, courseDao, userDao):
        self.courseInstructorDao = courseInstructorDao
        self.courseDao = courseDao
        self.userDao = userDao


    def assignInstructor(self, courseId, instructorId):
        course = self.courseDao.getCourseById(courseId)
        if not course:
            raise ValueError("Course not found")


        instructor = self.userDao.getUserById(instructorId)
        if not instructor:
            raise ValueError("Instructor not found")

        if instructor.role.role_name != "instructor":
            raise ValueError("Selected used is not an instructor")


        if self.courseInstructorDao.courseInstructorExists(courseId, instructorId):
            raise ValueError("Instrucotr is allrady assigned to this course")

        courseInstructor = CourseInstructor(
            course_id=courseId,
            instructor_id=instructorId
            
        )

        return self.courseInstructorDao.saveCourseInstructor(courseInstructor)


    def getCourseInstructorById(self, courseInstructorId):
        courseInstructor = self.courseInstructorDao.getCourseInstructorById(courseInstructorId)
        if not courseInstructor:
            raise ValueError("Course Instructor assignment not found")


        return courseInstructor


    def getInstructorsByCourseId(self, courseId):
        return self.courseInstructorDao.getInstructorsByCourseId(courseId)

    def getCoursesByInstructorId(self, instructorId):
        return self.courseInstructorDao.getCoursesByInstructorId(instructorId)

    def removeInstructor(self, courseInstructorId):
        courseInstructor = self.getCourseInstructorById(courseInstructorId)
        self.courseInstructorDao.deleteCourseInstructor(courseInstructor)



    def getAllInstructors(self):
        return self.userDao.getUsersByRole("instructor")


    def getAvailableInstructors(self, courseId):

        assignments = self.getInstructorsByCourseId(courseId)

        assignedInstructorIds = {
            assignment.instructor_id
            for assignment in assignments
        }

        instructors = self.userDao.getUsersByRole("instructor")

        return [
            instructor
            for instructor in instructors
            if instructor.id not in assignedInstructorIds
        ]