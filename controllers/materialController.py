import logging
from flask import(
    Blueprint,  render_template,
    redirect, send_file,
    url_for,
    jsonify,
    request,
    flash
)
from flask_jwt_extended import get_jwt_identity

from dao.courseInstructorDao import CourseInstructorDao
from forms.materialForms import MaterialForm
from dao.materialDao import MaterialDao
from dao.lessonDao import LessonDao
from services.materialService import MaterialService
from config.auth import roleRequired, wantsJson, loginRequired, getCurrentUserIdentity

logger = logging.getLogger(__name__)
materialBp = Blueprint("material", __name__)

materialDao = MaterialDao()
lessonDao = LessonDao()
courseInstructorDao = CourseInstructorDao()
materialService = MaterialService(materialDao, lessonDao)


@materialBp.route("/lessons/<int:lessonId>/materials", methods=["GET"])
@loginRequired
def listMaterials(lessonId):
    materials = materialService.getMaterialsByLessonId(lessonId)

    if wantsJson():
        return jsonify({
            "success": True,
            "materials": [material.toDict() for material in materials]
        })

    return render_template("material/materialList.html", materials=materials, lessonId=lessonId)


@materialBp.route("/lessons/<int:lessonId>/materials/upload", methods=["GET", "POST"])
@roleRequired("instructor")
def uploadMaterial(lessonId):
   
  
    lesson = lessonDao.getLessonById(lessonId)
    if not lesson:
        if wantsJson():
            return jsonify({"success": False, "message": "Lesson not found"}), 404
        flash("Lesson not found", "danger")
        return redirect(url_for("course.listCourses"))



    courseId = lesson.module.course_id
    userId = getCurrentUserIdentity()
    courseInstructor = courseInstructorDao.getByCourseAndInstructor(courseId, userId)
    if not courseInstructor:
        if wantsJson():
                return jsonify({"success": False, "message": "You are not assigned to teach this course"}), 403
        flash("You are not assigned to teach this course", "danger")
        return redirect(url_for("course.listCourses"))
        
    form = MaterialForm()
    if form.validate_on_submit():
        try:

            courseInstructorId = courseInstructor.id
            material = materialService.uploadMaterial(
                lessonId,
                courseInstructorId=courseInstructorId,
                fileStorage=form.file.data,
                access=form.access.data
            )
            logger.info("Material uploaded successfully: %s", material.file_name)

            if wantsJson():
                return jsonify({
                    "success": True,
                    "message": "Material uploaded successfully",
                    "material": material.toDict()
                }), 201

            flash("Material uploaded successfully", "success")
            return redirect(url_for("material.listMaterials", lessonId=lessonId))

        except ValueError as ve:
            logger.warning("Material upload validation failed")
            if wantsJson():
                return jsonify({
                    "success": False,
                    "message": str(ve)
                }), 400

            flash(str(ve), "danger")

        except Exception as e:
            logger.warning("An unexpected error occurred while material upload")
            if wantsJson():
                return jsonify({
                    "success": False,
                    "message": str(e)
                }), 400

            flash("An unexpected error occurred", "danger")

    if request.method == "POST" and wantsJson():
        return jsonify({
            "success": False,
            "errors": form.errors
        }), 400

    return render_template("material/materialForm.html", form=form, lessonId=lessonId, lesson=lesson)



@materialBp.route("/materials/<int:materialId>/download", methods=["GET"])
@loginRequired
def downloadMaterial(materialId):
    try:
        material = materialService.getMaterialById(materialId)
        return send_file(material.file_path, as_attachment=True)
    except ValueError as ve:
        logger.warning("Material download failed for id: %s", materialId)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(ve)
            }), 404

        flash(str(ve), "danger")
        return redirect(url_for("course.listCourses"))
    
    

    except Exception as e:
        logger.warning("Unexpected error during material download  for id: %s", materialId)

        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(e)
            }), 404

        flash("An unexpected error occurred while downloading material", "danger")
        return redirect(url_for("course.listCourses"))




@materialBp.route("/materials/<int:materialId>/delete", methods=["POST"])
@loginRequired
@roleRequired("instructor")
def deleteMaterial(materialId):
    try:
        material = materialService.getMaterialById(materialId)
        lessonId = material.lesson_id
        instructorId = int(get_jwt_identity())
        
          

        
        materialService.deleteMaterial(material, instructorId)
        logger.info("Material deleted successfully: %s", materialId)

        if wantsJson():
            return jsonify({
                "success": True,
                "message": "Material deleted successfully"
            })

        flash("Material deleted successfully", "success")
        
        return redirect(url_for("material.listMaterials", lessonId=lessonId))
    except ValueError as ve:
        logger.warning("Material deletion failed for id: %s", materialId)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(ve)
            }), 404

    except PermissionError as pe:
            logger.warning("Unauthorized material deletion for id %s", materialId)
            if wantsJson():
                return jsonify({
                    "success": False,
                    "message": str(pe)
                }), 403
    

            flash(str(pe), "danger")
     


    except Exception as e:
        logger.warning("Unexpected error during material deletion  for id: %s", materialId)

        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(e)
            }), 404

        flash("An unexpected error occurred while deleting material", "danger")

    return redirect(url_for("course.listCourses"))
   