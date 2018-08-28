from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError

from app.models import Admin


class LoginForm(FlaskForm):
    """
    管理员登录表单
    """
    account = StringField(
        label='用户名',
        validators=[
            DataRequired('用户名不能为空'),
        ],
        description='账号',
        render_kw={
            'class': 'form-control',
            'placeholder': '请输入账号!',
        }
    )

    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired('密码不能为空'),
            Length(min=6, max=12, message='密码长度必须6-12位')
        ],
        description='密码',
        render_kw={
            'class': 'form-control',
            'placeholder': '请输入密码',
        }
    )

    submit = SubmitField(
        '登录',
        render_kw={
            'class': "btn btn-primary btn-block btn-flat"
        }
    )


    def validate_account(self, filed):
        account = filed.data
        temp = Admin.query.filter_by(name=account).first()
        if temp == None:
            raise ValidationError('账号不存在')
