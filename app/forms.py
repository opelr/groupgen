from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SumbitField, TextAreaField


class ReturnGroupForm(FlaskForm):
    title = StringField(u"Groups")
    body = TextAreaField(u"", render_kw={"rows": 70, "cols": 11})
