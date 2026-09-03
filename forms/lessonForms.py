from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional



class LessonForm(FlaskForm):

    lessonName = StringField(
        "Lesson Name",
        validators=[DataRequired(), Length(min=2, max=150)]
    )

    content = TextAreaField(
        "Content",
        validators=[Optional()]
    )

    submit = SubmitField("Save Lesson")


class LessonUpdateForm(FlaskForm):

    lessonName = StringField(
        "Lesson Name",
        validators=[Optional(), Length(min=2, max=150)]
    )

    content = TextAreaField(
        "Content",
        validators=[Optional()]
    )

    submit = SubmitField("Save Lesson")