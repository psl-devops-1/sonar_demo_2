import os
import logging
from werkzeug.utils import secure_filename

from models.material import Material

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "mp4", "docx", "pptx"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024
UPLOAD_ROOT = "uploads"


class MaterialService:
    def __init__(self, materialDao, lessonDao):
        self.materialDao  = materialDao
        self.lessonDao = lessonDao


    def _getExtension(self, filename):
        if "." not in filename:
            return ""

        return filename.rsplit(".", 1)[1].lower()


    def uploadMaterial(self, lessonId, courseInstructorId,  fileStorage, access="public"):
        lesson = self.lessonDao.getLessonById(lessonId)
        if not lesson:
            raise ValueError("Lesson not found")

        fileName = secure_filename(fileStorage.filename)
        if not fileName:
            raise ValueError("Invalid filename")

        existingMaterial = self.materialDao.getByLessonAndFileName(lessonId, fileName)

        if existingMaterial:
            raise ValueError(
                "A material with this file name already exists for this lesson."
            )

        
        extension = self._getExtension(fileName)



        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError("File exceeds maximum allowed size")


        fileStorage.stream.seek(0, os.SEEK_END)
        fileSize = fileStorage.stream.tell()
        fileStorage.stream.seek(0)

        if fileSize > MAX_FILE_SIZE_BYTES:
            raise ValueError("File exceedes maximum allowed size of 50 MB")


        courseId = lesson.module.course_id
        moduleId = lesson.module_id


        targetDir = os.path.join(UPLOAD_ROOT, "courses", str(courseId), "modules", str(moduleId), "lessons", str(lessonId))
        os.makedirs(targetDir, exist_ok=True)

        filePath = os.path.join(targetDir, fileName)
        fileStorage.save(filePath)

        material = Material(
            lesson_id = lessonId,
            course_instructor_id =courseInstructorId,
            file_name=fileName,
            file_path=filePath,
            file_type=extension,
            access=access            
        )

        return self.materialDao.saveMaterial(material)


    def getMaterialById(self, materialId):
        material = self.materialDao.getMaterialById(materialId)
        if not material:
            raise ValueError("Material not found")
        return material


    def getMaterialsByLessonId(self, lessonId):
        return self.materialDao.getMaterialsByLessonId(lessonId)


    def deleteMaterial(self, material, instructorId):

        if material.course_instructor.instructor_id != instructorId:
            raise PermissionError("You are not authorized to delete this material")

        

        if os.path.exists(material.file_path):
            try:
                os.remove(material.file_path)
            except OSError:
                logger.exception("Failed to remove file from disk: %s", material.file_path)


        self.materialDao.deleteMaterial(material)
