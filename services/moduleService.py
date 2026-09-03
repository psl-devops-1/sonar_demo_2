
import logging
from models.module import Module

logger = logging.getLogger(__name__)

class ModuleService:

    def __init__(self, moduleDao, enrollmentDao):
        self.moduleDao = moduleDao
        self.enrollmentDao = enrollmentDao



    def createModule(self, courseId, moduleName, description=None):
        if self.moduleDao.moduleExistsByName(courseId,moduleName) or self.moduleDao.moduleExistsByName(courseId,moduleName.strip().lower()) :
            raise ValueError("A module with this name already exists in this course")

        module = Module(
            course_id=courseId,
            module_name=moduleName.strip(),
            description=description            
        )

        return self.moduleDao.saveModule(module)

    def getModuleById(self, moduleId):
        module = self.moduleDao.getModuleById(moduleId)
        if not module:
            raise ValueError("Module not found")

        return module


    def getModulesByCourseId(self, courseId):
        return self.moduleDao.getModulesByCourseId(courseId)


    def updateModule(self, moduleId,moduleName=None, description=None):
        module = self.getModuleById(moduleId)
        if moduleName and moduleName != module.module_name:
                              
            if self.moduleDao.moduleExistsByName(module.course_id, moduleName) or self.moduleDao.moduleExistsByName(module.course_id, moduleName.strip().lower()):
                raise ValueError("A module with this name already exists in this course")
            module.module_name = moduleName


        if description is not None:
            module.description = description

        return self.moduleDao.saveModule(module)


    def deleteModule(self, moduleId):
        module = self.getModuleById(moduleId)
        self.moduleDao.deleteModule(module)


    def getModulesByEnrollmentId(self, enrollmentId):
        enrollment = self.enrollmentDao.getEnrollmentById(enrollmentId)

        if not enrollment:
            raise ValueError("Enrollment not found")

        courseId = enrollment.course_instructor.course_id

        return self.moduleDao.getModulesByCourseId(courseId)