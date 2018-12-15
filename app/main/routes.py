from flask import render_template, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
import json
from datetime import datetime

from app import db
from app.main.forms import SeatingChartForm, SaveForm, LoadForm
from app.main.backend import (
    create_seating_chart,
    render_output,
    store_display,
    form_to_function,
    form_to_model,
    model_to_form,
)
from app.models import User, Group, GroupConfig
from app.main import bp


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
def index():
    output_text = ""
    form = SeatingChartForm()

    try:
        session_form = session["group_generation_form"]
    except KeyError:
        session_form = None

    if request.method == "GET":
        if session_form is not None:
            form.individuals.data = session["group_generation_form"]["names"]
            form.together.data = session["group_generation_form"]["together"]
            form.separate.data = session["group_generation_form"]["apart"]
            form.num_groups.data = session["group_generation_form"]["num_groups"]
            form.max_size.data = session["group_generation_form"]["max_size"]
            session["group_generation_form"] = None

    if request.method == "POST":
        if form.validate_on_submit():

            session["group_generation_form"] = {
                "names": form.individuals.data,
                "together": form.together.data,
                "apart": form.separate.data,
                "num_groups": form.num_groups.data,
                "max_size": form.max_size.data,
            }

            indiv = form_to_function(
                    session["group_generation_form"]["names"], "individuals"
                )
            together = form_to_function(
                    session["group_generation_form"]["together"], "groupings"
                )
            separate =form_to_function(
                    session["group_generation_form"]["apart"], "groupings"
                ) 
            num_groups = form_to_function(
                    session["group_generation_form"]["num_groups"], "integers"
                )
            max_size = form_to_function(
                    session["group_generation_form"]["max_size"], "integers"
                )

            seating_chart = create_seating_chart(
                names=indiv,
                together=together,
                apart=separate,
                num_groups=num_groups,
                max_size=max_size,
            )
            output_text = render_output(seating_chart)

    return render_template(
        "index.html", title="Home", form=form, output_text=output_text
    )


@bp.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    groups = user.groups.order_by(Group.creation_time.desc())
    return render_template("user.html", user=user, groups=groups)


@bp.route("/save/", methods=["GET", "POST"])
def save():
    form = SaveForm()

    if current_user.is_anonymous:
        flash("Need to log in")
        return redirect(url_for("main.index"))

    if session["group_generation_form"] is None:
        flash("No generated group data!")
        return redirect(url_for("main.index"))

    if request.method == "GET":
        return render_template(
            "save_group.html",
            title="Save Group",
            form=form,
            username=current_user.username,
        )

    if request.method == "POST":
        if form.validate_on_submit() and session["group_generation_form"] is not None:
            user = User.query.filter_by(username=current_user.username).first()

            print(f"Names: {session['group_generation_form']['names']}")

            group = Group(
                title=form.title.data,
                individuals=form_to_model(session["group_generation_form"]["names"], "individuals"),
                indiv_display=store_display(session["group_generation_form"]["names"]),
                creation_time=datetime.utcnow(),
                user_id=user.id,
            )
            db.session.add(group)
            db.session.commit()

            groupconfig = GroupConfig(
                pairs=form_to_model(session["group_generation_form"]["together"], "groupings"),
                separated=form_to_model(session["group_generation_form"]["apart"], "groupings"),
                max_size=session["group_generation_form"]["max_size"],
                num_groups=session["group_generation_form"]["num_groups"],
                user_id=user.id,
                group_id=group.id,
            )
            db.session.add(groupconfig)
            db.session.commit()

            session["group_generation_form"] = None
            flash("Group saved!")
        return redirect(url_for("main.user", username=current_user.username))

    return render_template("save_group.html", title="Save Group", form=form)


@bp.route("/delete/<group>", methods=["GET"])
def delete(group):
    user = User.query.filter_by(username=current_user.username).first_or_404()
    del_group = user.groups.filter_by(title=group).first()
    db.session.delete(del_group)
    db.session.commit()
    flash("Group removed!")
    return redirect(url_for("main.user", username=current_user.username))


@bp.route("/load/<group>", methods=["GET"])
def load(group):
    user = User.query.filter_by(username=current_user.username).first_or_404()
    group_obj = user.groups.filter_by(title=group).first()
    group_config = group_obj.config.first()

    session["group_generation_form"] = {
        "names": model_to_form(group_obj.individuals, "individuals"),
        "together": model_to_form(group_config.pairs, "groupings"),
        "apart": model_to_form(group_config.separated, "groupings"),
        "max_size": model_to_form(group_config.max_size, "integers"),
        "num_groups": model_to_form(group_config.num_groups, "integers"),
    }
    flash("Group successfully loaded!")
    return redirect(url_for("main.index"))


@bp.route("/about")
def about():
    return render_template("about.html")
