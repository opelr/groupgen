from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import db
from app.main.forms import SeatingChartForm, SaveForm, LoadForm
from app.main.backend import (
    create_seating_chart,
    handle_form_individuals,
    handle_form_groupings,
    handle_form_integer,
    render_output,
)
from app.models import User
from app.main import bp


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
def index():
    output_text = ""
    form = SeatingChartForm()
    saveform = SaveForm()
    loadform = LoadForm()
    if form.validate_on_submit():
        indiv = handle_form_individuals(form.individuals.data)
        together = handle_form_groupings(form.together.data)
        separate = handle_form_groupings(form.separate.data)
        max_groups = handle_form_integer(form.max_groups.data)
        max_indiv = handle_form_integer(form.max_indiv.data)

        seating_chart = create_seating_chart(
            names=indiv,
            together=together,
            apart=separate,
            max_size=max_indiv,
            max_tables=max_groups,
        )
        output_text = render_output(seating_chart)
    return render_template(
        "index.html",
        title="Home",
        form=form,
        output_text=output_text,
        saveform=saveform,
        loadform=loadform,
    )


@bp.route("/user/<username>")
@login_required
def user(username):
    # TODO: Add basic user information
    # TODO: Add ability to change user information (email, password, etc.)
    # TODO: List number of saved groups, last login, next to gravatar
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("user.html", user=user)


@bp.route("/about")
def about():
    return render_template("about.html")
