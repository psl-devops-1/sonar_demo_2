from flask_wtf import FlaskForm
from flask_wtf.file import  FileField, FileRequired, FileAllowed
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


ALLOWED_EXTENSIONS = ["pdf", "png", "jpg", "jpeg", "mp4", "docx", "pptx"]

class MaterialForm(FlaskForm):

    """  fileName = StringField(
        "File Name",
        validators=[DataRequired(), Length(min=2, max=150)]
    )
 `  """
    
    file = FileField(
        "File",
        validators=[
            FileRequired(),
            FileAllowed(ALLOWED_EXTENSIONS, "File type not allowed")
        ]
    )

    access = SelectField(
        "Access",
        choices=[("public", "Public"), ("enrolled", "Enrolled Only")],
        default="public"
    )

    submit = SubmitField("Upload Material")

