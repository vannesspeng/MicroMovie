from . import home
from flask import render_template


@home.route('/')
def index():
    return render_template("home/index.html")


@home.route('/login/')
def login():
    return render_template('home/login.html')


@home.route('/logout/')
def logout():
    return render_template('home/login.html')
