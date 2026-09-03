import logging

from models.lesson import Lesson
logger = logging.getLogger(__name__)


class LessonService:

    def __init__(self, lessonDao, enrollmentDao, moduleDao):
        self.lessonDao = lessonDao
        self.enrollmentDao = enrollmentDao
        self.moduleDao = moduleDao



    def createLesson(self, moduleId, lessonName, content=None):
        if self.lessonDao.lessonExistsByName(moduleId, lessonName) or self.lessonDao.lessonExistsByName(moduleId, lessonName.lower()):
            raise ValueError("A lesson with this name already exists in this module")

        lesson = Lesson(
            module_id=moduleId,
            lesson_name=lessonName,
            content=content            
        )

        return self.lessonDao.saveLesson(lesson)


    def getLessonById(self, lessonId):
        lesson = self.lessonDao.getLessonById(lessonId)
        if not lesson:
            raise ValueError("Lesson not found")

        return lesson


    def getLessonByModuleId(self, moduleId):
        return self.lessonDao.getLessonByModuleId(moduleId)


    def updateLesson(self, lessonId, lessonName=None, content=None):
        lesson = self.getLessonById(lessonId)

        if lessonName and lessonName != lesson.lesson_name:
            if self.lessonDao.lessonExistsByName(lesson.module_id, lessonName) or self.lessonDao.lessonExistsByName(lesson.module_id, lessonName.lower()):
                raise ValueError("A lesson witht this name already exists in the moudles")
            lesson.lesson_name = lessonName.strip()


        if content is not None:
            lesson.content = content.strip()


        return self.lessonDao.saveLesson(lesson)


    def deleteLesson(self, lessonId):
        lesson = self.getLessonById(lessonId)
        self.lessonDao.deleteLesson(lesson)



    def getLessonsByEnrollmentAndModule(self, enrollmentId, moduleId):

        enrollment = self.enrollmentDao.getEnrollmentById(enrollmentId)

        if not enrollment:
            raise ValueError("Enrollment not found")

        courseId = enrollment.course_instructor.course_id

        module = self.moduleDao.getModuleById(moduleId)

        if not module:
            raise ValueError("Module not found")

       


        if module.course_id != courseId:
            raise ValueError(
                "This module does not belong to your enrolled course"
            )

        return self.lessonDao.getLessonByModuleId(moduleId)



    def getLessonByEnrollment(self,enrollmentId, lessonId):

        enrollment = self.enrollmentDao.getEnrollmentById(
            enrollmentId
        )

        if not enrollment:
            raise ValueError("Enrollment not found")

        lesson = self.lessonDao.getLessonById(
            lessonId
        )

        if not lesson:
            raise ValueError("Lesson not found")

        courseId = enrollment.course_instructor.course_id

        lessonCourseId = lesson.module.course_id

        if lessonCourseId != courseId:
            raise ValueError(
                "This lesson does not belong to your enrolled course"
            )

        return lesson