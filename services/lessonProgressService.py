import logging

from config.auth import getCurrentUserIdentity
from models.lessonProgress import LessonProgress

logger = logging.getLogger(__name__)

class LessonProgressService:

    def __init__(self, lessonProgressDao, enrollmentDao):
        self.lessonProgressDao = lessonProgressDao
        self.enrollmentDao = enrollmentDao


    def markLessonComplete(self, enrollmentId, lessonId, completed=True):

        enrollment = self.enrollmentDao.getEnrollmentById(enrollmentId)
        userId = int(getCurrentUserIdentity())
        if userId != enrollment.student_id:
            logger.warning(
                "Unauthorized lesson completion attempt: User ID %s tried to access Student ID %s's enrollment (Enrollment ID: %s)",
                userId,
                enrollment.student_id,
                enrollment.id
            )
                    
            raise PermissionError("You are not authorized to complete this lesson")

        #add check for lesson belongs to enrolled course
       
        progress = self.lessonProgressDao.getProgressByEnrollmentAndLesson(
            enrollmentId, lessonId
        )

        if progress:
            raise ValueError("Lesson already marked as completed")

        progress = LessonProgress(
            enrollment_id=enrollmentId,
            lesson_id=lessonId,
            completed=completed                
        )
        

        res = self.lessonProgressDao.saveProgress(progress)
        completedCount, totalCount = self.lessonProgressDao.getCompletionStats(enrollmentId)
        if completedCount == totalCount and totalCount > 0:
            enrollment = self.enrollmentDao.updateStatus(enrollmentId, "completed")
        elif completedCount >= 1:
            enrollment = self.enrollmentDao.updateStatus(enrollmentId, "ongoing")
        
         
        return res
        

    



    def getProgressByEnrollmentId(self, enrollmentId):
        return self.lessonProgressDao.getProgressByEnrollmentId(enrollmentId)


    def getProgressForLesson(self, enrollmentId, lessonId):
        return self.lessonProgressDao.getProgressByEnrollmentAndLesson(
            enrollmentId,
            lessonId
        )