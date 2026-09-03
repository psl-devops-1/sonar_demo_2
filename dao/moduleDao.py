from config.database import db
from models.module import Module


class ModuleDao:

    def getModuleById(self, moduleId):
        return db.session.get(Module, moduleId)

    def getModulesByCourseId(self, courseId):
        return Module.query.filter_by(
            course_id=courseId
        ).order_by(Module.id).all()


    def saveModule(self, module):
        db.session.add(module)
        db.session.commit()
        return module


    def deleteModule(self, module):
        db.session.delete(module)
        db.session.commit()



    def moduleExistsByName(self, courseId, moduleName):
        return Module.query.filter_by(
            course_id=courseId,
            module_name=moduleName
        ).first() is not None