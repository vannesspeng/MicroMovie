from flask import Flask, render_template

app = Flask(__name__)
app.debug = True


from app.admin import admin as admin_blueprint
from app.home import home as home_blueprint
#1、注册蓝图
app.register_blueprint(admin_blueprint, url_prefix="/admin")
app.register_blueprint(home_blueprint)

@app.errorhandler(404)
def page_not_found(error):
    """
    404
    """
    return render_template("home/404.html"), 404