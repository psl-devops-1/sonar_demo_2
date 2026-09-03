import logging
from flask import(
    Blueprint,
    render_template,
    redirect,
    url_for,
    jsonify,
    request,
    flash
)
from dao.enrollmentDao import EnrollmentDao
from forms.moduleForms import ModuleForm, ModuleUpdateForm
from dao.moduleDao import ModuleDao
from models import module
from services.moduleService import ModuleService
from config.auth import wantsJson, loginRequired, roleRequired

logger = logging.getLogger(__name__)
moduleBp = Blueprint("module", __name__)
moduleDao = ModuleDao()
enrollmentDao = EnrollmentDao()
moduleService = ModuleService(moduleDao=moduleDao, enrollmentDao=enrollmentDao)


@moduleBp.route("/courses/<int:courseId>/modules", methods=["GET"])
@loginRequired
def listModules(courseId):
    modules  = moduleService.getModulesByCourseId(courseId)
    if wantsJson():
        return jsonify({
            "success": True,
            "modules": [module.toDict() for module in modules]
        })

    return render_template("module/moduleList.html", modules=modules, courseId=courseId)


@moduleBp.route("/courses/<int:courseId>/modules/create", methods=["GET","POST"])
@roleRequired("admin")
def createModule(courseId):
    form = ModuleForm()

    if form.validate_on_submit():
        try:
            module = moduleService.createModule(
                courseId,
                moduleName=form.moduleName.data,
                description=form.description.data
            )

            logger.info("Module created successfully: %s", module.module_name)

            if wantsJson():
                return jsonify({
                    "success": True,
                    "message": "Module created successfully",
                    "module": module.toDict()
                }), 201


            flash("Module created successfully", "success")
            return redirect(url_for("module.listModules", courseId=courseId))

        except ValueError as ve:
            logger.warning("Module creation validation failed")
            if wantsJson():
                return jsonify({"success": False, "message":str(ve)}), 400

            flash(str(ve), "danger")

        except Exception as e:
            logger.exception("Unexcpected error during module creation")
            if wantsJson():
                return jsonify({"success": False, "message": str(e)}), 400
            flash("An unexpected error occured", "danger")

    if request.method == "POST" and wantsJson():
        return jsonify({
            "success": False,
            "errors": form.errors
        }), 400


    return render_template("module/moduleForm.html", form=form, courseId=courseId)

   


@moduleBp.route("/modules/<int:moduleId>/update", methods=["GET", "POST"])
@roleRequired("admin")
def updateModule(moduleId):
    form = ModuleUpdateForm()

    try:
        existingModule = moduleService.getModuleById(moduleId)
        courseId = getattr(existingModule, "courseId", getattr(existingModule, "course_id", None))
    except Exception as e:
        flash("Module not found", "danger")
        return redirect(url_for("course.listCourses"))

    if request.method == "GET":
        form.moduleName.data = getattr(existingModule, "moduleName", getattr(existingModule, "module_name", ""))
        form.description.data = existingModule.description
        

    if form.validate_on_submit():
        try:
            module = moduleService.updateModule(
                moduleId,
                moduleName=form.moduleName.data,
                description=form.description.data
            )
            logger.info("Module updated successfully: %s",module.module_name)


            if wantsJson():
                return jsonify({
                    "success": True,
                    "message": "Module updated successfully",
                    "module": module.toDict()
                })

            flash("Module updated successfully", "success")
            return redirect(url_for("module.listModules", courseId=module.course_id))

        except ValueError as ve:
            logger.warning("Module update validation failed for id %s", moduleId)
            if wantsJson():
                return jsonify({"success": False, "message": str(ve)}), 400
            flash(str(ve), "danger")

        except Exception as e:
            logging.exception("Unexpected error during module update for id %s", moduleId)
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

    return render_template("module/moduleForm.html", form=form, courseId=courseId)


@moduleBp.route("/modules/<int:moduleId>/delete", methods=["POST"])
@roleRequired("admin")
def deleteModule(moduleId):
    courseId = None
    try:
        module = moduleService.getModuleById(moduleId)
        courseId = getattr(module, "courseId", getattr(module, "course_id", None))
        moduleService.deleteModule(moduleId)
        logger.info("Module deleted successfully: %s", moduleId)

        if wantsJson():
            return jsonify({
                "success": True,
                "message": "Module deleted successfully"
            })

        flash("Module deleted successfully", "success")

    except ValueError as ve:
        logger.warning("Module delete failed for id %s", moduleId)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(ve)
            }), 404

        flash(str(ve), "danger")

    except Exception as e:
        logger.exception("Unexpected error during module deletion for id %s", moduleId)
        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

        flash("An unexpected error occured", "danger")

    if courseId:
        return redirect(url_for("module.listModules", courseId=courseId))
    return redirect(url_for("course.listCourses"))





@moduleBp.route(
    "/enrollments/<int:enrollmentId>/modules",
    methods=["GET"]
)
@roleRequired("student")
def listEnrolledModules(enrollmentId):

    try:
        modules = moduleService.getModulesByEnrollmentId(enrollmentId)

        if wantsJson():
            return jsonify({
                "success": True,
                "modules": [module.toDict() for module in modules]
            })

        return render_template(
            "module/moduleList.html",
            modules=modules,
            enrollmentId=enrollmentId
        )

    except ValueError as ve:
        logger.warning(
            "Could not load modules for enrollment %s",
            enrollmentId
        )

        if wantsJson():
            return jsonify({
                "success": False,
                "message": str(ve)
            }), 404

        flash(str(ve), "danger")
        return redirect(url_for("enrollment.listMyEnrollments"))

    except Exception:
        logger.exception(
            "Unexpected error loading modules for enrollment %s",
            enrollmentId
        )

        if wantsJson():
            return jsonify({
                "success": False,
                "message": "Could not load course modules"
            }), 400

        flash("Could not load course modules", "danger")
        return redirect(url_for("enrollment.listMyEnrollments"))