from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    PasswordField,
    BooleanField,
    IntegerField,
    SubmitField,
)
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User

import re


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("User Name", validators=[DataRequired()])
    firstname = StringField("First Name", validators=[DataRequired()])
    lastname = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")


class SeatingChartForm(FlaskForm):
    tf_rows_long = 10
    tf_rows_short = 5
    tf_cols = 26
    indiv_placehold = (
        "Alice\nBob\nCarly\nDion\nEesha\nFrank\nGrace\nHerman\nIzzie\nJames"
    )
    togeth_placehold = "Alice, Dion\nFrank, James"
    separ_placehold = "Carly, Frank\nCarly, James"

    individuals = TextAreaField(
        "Individuals",
        render_kw={
            "placeholder": indiv_placehold,
            "rows": tf_rows_long,
            "cols": tf_cols,
        },
    )
    together = TextAreaField(
        "Grouped pairs",
        render_kw={
            "placeholder": togeth_placehold,
            "rows": tf_rows_short,
            "cols": tf_cols,
        },
    )
    separate = TextAreaField(
        "Separated pairs",
        render_kw={
            "placeholder": separ_placehold,
            "rows": tf_rows_short,
            "cols": tf_cols,
        },
    )
    max_groups = IntegerField("Max. number of groups", default=0)
    max_indiv = IntegerField("Max. individuals per group", default=0)
    submit = SubmitField("Generate")

    def validate_individuals(self, individuals):
        indiv = re.split("[,;\n\r]+", individuals.data)
        if len(indiv) <= 1:
            raise ValidationError("Please enter more than one individual.")
        
        if not any(sep in individuals.data for sep in [",", ";", "\n", "\r"]):
            raise ValidationError(
                "Please separate individuals on new lines."
            )


    def validate_together(self, together):
        individuals = re.split("[,;\n\r]+", self.individuals.data)
        together = re.split("[,;\n\r]+", together.data)
        together_indiv = list(set([i.strip() for i in together]))
        all_present = all([i in individuals for i in together_indiv])

        if not all_present:
            raise ValidationError("All persons must be included in Individuals")

    def validate_separate(self, separate):
        individuals = list(filter(None, re.split("[,;\n\r]+", self.individuals.data)))
        separate = filter(None, re.split("[,;\n\r]+", separate.data))
        separate_indiv = list(set([i.strip() for i in separate]))
        all_present = all([i in individuals for i in separate_indiv])

        if not all_present:
            raise ValidationError("All persons must be included in Individuals")

    def validate_max_groups(self, max_groups):
        if max_groups.data < 0:
            raise ValidationError("Must be zero or positive number")

    def validate_max_indiv(self, max_indiv):
        if max_indiv.data < 0:
            raise ValidationError("Must be zero or positive number")
