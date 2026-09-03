from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    TextAreaField,
    IntegerField,
    SelectField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    NumberRange
)


class QuizForm(FlaskForm):
    quizName = StringField(
        "Quiz Name",
        validators=[
            DataRequired(),
            Length(min=2, max=150)
        ]
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=2000)
        ]
    )

    submit = SubmitField("Save Quiz")


class QuestionForm(FlaskForm):
    questionText = TextAreaField(
        "Question",
        validators=[
            DataRequired(),
            Length(min=2, max=2000)
        ]
    )

    option1 = StringField("Option 1", validators=[DataRequired(), Length(max=255)])
    option2 = StringField("Option 2", validators=[DataRequired(), Length(max=255)])
    option3 = StringField("Option 3", validators=[Optional(), Length(max=255)])
    option4 = StringField("Option 4", validators=[Optional(), Length(max=255)])

    correctOption = SelectField(
        "Correct Option",
        choices=[
            ("option1", "Option 1"),
            ("option2", "Option 2"),
            ("option3", "Option 3"),
            ("option4", "Option 4")
        ]
    )

    points = IntegerField(
        "Points",
        default=1,
        validators=[
            DataRequired(),
            NumberRange(min=1, max=100)
        ]
    )

    submit = SubmitField("Add Question")