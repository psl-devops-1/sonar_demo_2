from flask_wtf import FlaskForm

from wtforms import(
    StringField,
    TextAreaField,
    SubmitField
)


from wtforms.validators import(
    DataRequired,
    Length,
    Optional
)

class CourseForm(FlaskForm):
    courseName = StringField(
        "Course Name",
        validators=[
            DataRequired(),
            Length(min=2, max=150)
        ]
    )

    description= TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=2000)

        ]
    )

    submit = SubmitField("Save Course")



class CourseUpdateForm(FlaskForm):
    courseName = StringField(
        "Course Name",
        validators=[
            Optional(),
            Length(min=2, max=150)
        ]
    )

    description= TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=2000)

        ]
    )

    submit = SubmitField("Save Course")
    
    