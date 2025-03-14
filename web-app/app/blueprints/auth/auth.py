from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.extensions import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully!", category="success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home.home"))
        else:
            flash("Invalid username or password.", category="error")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", category="info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        valid_roles = {"admin", "viewer", "editor"}
        if role not in valid_roles:
            flash(
                "Invalid role selected. Please choose Admin, Viewer, or Editor.",
                category="error",
            )
            return render_template("auth/register.html")

        if User.query.filter_by(username=username).first():
            flash(
                "Username already exists. Please choose a different one.",
                category="error",
            )
        else:
            hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
            new_user = User(
                username=username, password=hashed_password, global_role=role
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash("Account created successfully!", category="success")
            return redirect(url_for("home.home"))

    return render_template("auth/register.html")


@auth_bp.route("/profile")
@login_required
def profile():
    profile_picture_url = f"https://robohash.org/{current_user.username}.png"
    return render_template(
        "auth/profile.html", user=current_user, profile_picture_url=profile_picture_url
    )
