from flask import render_template, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
import json
from datetime import datetime

from app import db
from app.main.forms import SeatingChartForm, SaveForm, LoadForm
from app.main.backend import (
    create_seating_chart,
    handle_form_individuals,
    handle_form_groupings,
    handle_form_integer,
    render_output,
    store_display,
)
from app.models import User, Group, GroupConfig
from app.main import bp


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
def index():
    output_text = ""
    form = SeatingChartForm()

    if form.validate_on_submit():
        indiv = handle_form_individuals(form.individuals.data)
        together = handle_form_groupings(form.together.data)
        separate = handle_form_groupings(form.separate.data)
        num_groups = handle_form_integer(form.num_groups.data)
        max_size = handle_form_integer(form.max_size.data)

        seating_chart = create_seating_chart(
            names=indiv,
            together=together,
            apart=separate,
            max_size=max_size,
            num_groups=num_groups,
        )
        output_text = render_output(seating_chart)

        ## Save form in session
        session["group_generation_form"] = {
            "names": indiv,
            "together": together,
            "apart": separate,
            "max_size": max_size,
            "num_groups": num_groups,
        }
    return render_template(
        "index.html",
        title="Home",
        form=form,
        output_text=output_text,
    )


@bp.route("/user/<username>")
@login_required
def user(username):
    # TODO: Add basic user information
    # TODO: Add ability to change user information (email, password, etc.)
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
            "save_group.html", title="Save Group", form=form, username=current_user.username
        )

    if request.method == "POST":
        if form.validate_on_submit() and session["group_generation_form"] is not None:
            user = User.query.filter_by(username=current_user.username).first()

            group = Group(
                title=form.title.data,
                individuals=json.dumps(session["group_generation_form"]["names"]),
                indiv_display=store_display(session["group_generation_form"]["names"]),
                creation_time=datetime.utcnow(),
                user_id=user.id,
            )
            db.session.add(group)
            db.session.commit()

            groupconfig = GroupConfig(
                pairs=json.dumps(session["group_generation_form"]["together"]),
                separated=json.dumps(session["group_generation_form"]["apart"]),
                max_size=json.dumps(session["group_generation_form"]["max_size"]),
                num_groups=json.dumps(session["group_generation_form"]["num_groups"]),
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


@bp.route("/about")
def about():
    return render_template("about.html")
