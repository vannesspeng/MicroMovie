from flask import Blueprint

# 1、定义蓝图
admin = Blueprint("admin", __name__)

import app.admin.views