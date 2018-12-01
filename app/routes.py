from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, SeatingChartForm
from app.models import User
from app.backend import (
    create_seating_chart,
    handle_form_individuals,
    handle_form_groupings,
    handle_form_integer,
    render_output,
)


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    output_text = ""
    form = SeatingChartForm()
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
    return render_template("index.html", title="Home", form=form, output_text=output_text)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Log In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Thanks for signing up!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("user.html", user=user)
