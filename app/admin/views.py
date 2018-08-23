from flask import render_template, redirect, url_for

from . import admin

@admin.route('/')
def index():
    return render_template("admin/index.html")


@admin.route("/login/")
def login():
    """
    后台登录
    """
    return render_template("admin/login.html")


@admin.route("/logout/")
def logout():
    """
    后台注销登录
    """
    return redirect(url_for("admin.login"))

@admin.route("/pwd/")
def pwd():
    """
    后台登录
    """
    return render_template("admin/pwd.html")


