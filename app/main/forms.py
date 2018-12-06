from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, SubmitField
from wtforms.validators import ValidationError
from app.models import User

import re


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
    num_groups = IntegerField("Number of groups", default=0)
    max_size = IntegerField("Maximum group size (individuals per group)", default=0)
    submit = SubmitField("Generate")

    def validate_individuals(self, individuals):
        indiv = re.split("[,;\n\r]+", individuals.data)
        if len(indiv) <= 1:
            raise ValidationError("Please enter more than one individual.")

        if not any(sep in individuals.data for sep in [",", ";", "\n", "\r"]):
            raise ValidationError("Please separate individuals on new lines.")

    def validate_together(self, together):
        individuals = re.split("[,;\n\r]+", self.individuals.data)
        together = re.split("[,;\n\r]+", together.data)
        together_indiv = list(set([i.strip() for i in together]))
        
        all_present = True
        if together != [""]:
            all_present = all([i in individuals for i in together_indiv])

        # all_present = all([i in individuals for i in together_indiv])

        if not all_present:
            raise ValidationError("All persons must be included in Individuals")

    def validate_separate(self, separate):
        individuals = list(filter(None, re.split("[,;\n\r]+", self.individuals.data)))
        separate = filter(None, re.split("[,;\n\r]+", separate.data))
        separate_indiv = list(set([i.strip() for i in separate]))
        all_present = all([i in individuals for i in separate_indiv])

        if not all_present:
            raise ValidationError("All persons must be included in Individuals")

    def validate_num_groups(self, num_groups):
        if num_groups.data < 0:
            raise ValidationError("Must be zero or positive number")

    def validate_max_size(self, max_size):
        if max_size.data < 0:
            raise ValidationError("Must be zero or positive number")


class SaveForm(FlaskForm):
    submit = SubmitField("Save")


class LoadForm(FlaskForm):
    submit = SubmitField("Load")
