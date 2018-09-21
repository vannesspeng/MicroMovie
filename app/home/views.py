import os
import uuid
from functools import wraps

from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from app import db, app
from app.home.forms import PwdForm, CommentForm
from app.admin.views import change_filename
from app.home.forms import RegistForm, LoginForm, UserdetailForm
from app.models import User, Userlog, Preview, Tag, Movie, Comment, Moviecol
from . import home
from flask import render_template, redirect, url_for, flash, session, request


# 登录检查装饰器
def user_log_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("home.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@home.route('/<int:page>/', methods=['GET'])
@home.route("/", methods=["GET"])
def index(page=None):
    tags = Tag.query.all()
    page_data = Movie.query
    # 处理标签参数
    tid = request.args.get('tid')
    if tid and tid != "None":
        page_data = page_data.filter_by(tag_id=int(tid))

    #处理星级参数
    star = request.args.get('star')
    if star and star != "None":
        page_data = page_data.filter_by(star=int(star))

    # 时间
    time = request.args.get('time')
    if  time and time != "None":
        if int(time) == 1:
            page_data = page_data.order_by(
                Movie.addtime.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.addtime.asc()
            )

    # 播放量的问题
    pm = request.args.get('pm')
    if pm and pm != "None":
        if int(pm) == 1:
            page_data = page_data.order_by(
                Movie.playnum.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.playnum.asc()
            )

    # 评论量
    cm = request.args.get("cm")
    if cm and cm != "None":
        if int(cm) == 1:
            page_data = page_data.order_by(
                Movie.commentnum.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.commentnum.asc()
            )

    if page is None:
        page = 1
    page_data = page_data.paginate(page=page, per_page=8)
    p = dict(
        tid=tid,
        star=star,
        time=time,
        pm=pm,
        cm=cm,
    )

    return render_template("home/index.html", tags=tags, p=p, page_data=page_data)

@home.route('/animation/')
def animation():
    data = Preview.query.all()
    return render_template('home/animation.html', data=data)

@home.route('/login/', methods=['GET', 'POST'])
def login():
    """
    登陆
    """
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=data['name']).first()
        if not user:
            flash("用户名错误，请重新输入!", category="err")
            return redirect(url_for("home.login"))

        if not user.check_pwd(data['pwd']):
            flash("密码错误，请重新输入!", category="err")
            return redirect(url_for("home.login"))
        session['user'] = user.name
        session['user_id'] = user.id
        userlog = Userlog(
            user_id=user.id,
            ip=request.remote_addr
        )
        db.session.add(userlog)
        db.session.commit()
        next = request.args.get('next')
        if not next or not next.startswith('/'):
            next = url_for('home.index')
        return redirect(next)
    return render_template('home/login.html', form=form)


@home.route('/logout/')
def logout():
    """
    退出
    """
    session.pop('user')
    session.pop('user_id')
    return redirect(url_for('home.login'))
#重定向到home模块下的登录


@home.route('/register/', methods=["GET", "POST"])
def register():
    """
    注册
    """
    form = RegistForm()
    if form.validate_on_submit():
        data = form.data
        user = User(
            name = data['name'],
            pwd= generate_password_hash(data['pwd']),
            email = data['email'],
            phone = data['phone'],
            uuid = uuid.uuid4().hex
        )
        db.session.add(user)
        db.session.commit()
        flash("注册成功!", category="ok")
        return redirect(url_for('home.index'))
    return render_template('home/register.html', form=form)

@home.route("/user/", methods=["GET", "POST"])
@user_log_req
def user():
    """
    用户中心
    """
    form = UserdetailForm()
    user = User.query.get_or_404(session['user_id'])
    if request.method == 'GET':
        form.info.data = user.info

    if form.validate_on_submit():
        data = form.data
        # 校验用户名，邮箱，手机号码是否已经存在
        name_count = User.query.filter_by(name=data['name']).count()
        if data['name'] != user.name and name_count == 1:
            flash('昵称已经存在!', category='err')
            return redirect(url_for('home.user'))

        email_count = User.query.filter_by(email=data['email']).count()
        if data['email'] != user.email and email_count == 1:
            flash('邮箱地址已经存在!', category='err')
            return redirect(url_for('home.user'))

        phone_count = User.query.filter_by(phone=data['phone']).count()
        if data['phone'] != user.phone and phone_count == 1:
            flash('手机号码已经存在',category='err')
            return redirect(url_for('home.user'))

        # 保存头像文件
        if not os.path.exists(app.config['FC_DIR']):
            os.mkdirs(app.config['FC_DIR'])
            os.chmod(app.config['FC_DIR'], 'rw')

        if form.face.data.filename != None:
            filename = secure_filename(form.face.data.filename)
            user.face = change_filename(filename)
            form.face.data.save(app.config['FC_DIR'] + user.face)


        user.name = data['name']
        user.email = data['email']
        user.phone = data['phone']
        user.info = data['info']
        # 上传头像

        db.session.add(user)
        db.session.commit()
        flash("用户信息更新成功!", category="ok")
        return redirect(url_for('home.user'))
    return render_template("home/user.html", form=form, user=user)


@home.route("/pwd/", methods=['GET', 'POST'])
def pwd():
    """
    修改密码
    """
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        # 判断旧密码是否正确
        user = User.query.get_or_404(session['user_id'])
        if not user.check_pwd(data['old_pwd']):
            flash("旧密码输入错误!",category='err')
            return redirect(url_for("home.pwd"))
        user.pwd = generate_password_hash(data['new_pwd'])
        db.session.add(user)
        db.session.commit()
        flash("密码修改成功!", category="ok")
        return redirect(url_for("home.logout"))
    return render_template("home/pwd.html", form=form)


@home.route("/comments/<int:page>/", methods=['GET'])
def comments(page=None):
    """
    评论记录
    """
    if page is None:
        page = 1
    page_data = Comment.query.join(Movie).join(User).filter(
        Movie.id == Comment.movie_id,
        User.id == session['user_id']
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=8)
    return render_template("home/comments.html", page_data=page_data)


@home.route("/loginlog/<int:page>/", methods=['GET'])
@user_log_req
def loginlog(page=None):
    """
    登录日志
    """
    if page is None:
        page = 1
    page_data = Userlog.query.filter_by(
        user_id=int(session['user_id'])
    ).order_by(
        Userlog.addtime.desc()
    ).paginate(page=page, per_page=8)
    return render_template("home/loginlog.html", page_data=page_data)


@home.route("/moviecol/", methods=['GET'])
def moviecol(page=None):
    """
    收藏电影
    """
    if page is None:
        page = 1
    page_data = Moviecol.query.join(Movie).join(User).filter(
        Movie.id == Moviecol.movie_id,
        User.id == session['user_id']
    ).order_by(
        Moviecol.addtime.desc()
    ).paginate(page=page, per_page=8)
    return render_template('home/moviecol.html', page_data=page_data)

@home.route("/moviecol/add/", methods=['GET', 'POST'])
def moviecol_add():
    """
    收藏电影
    """
    import json
    uid = request.args.get("uid", "")
    mid = request.args.get("mid", "")

    if (uid is None) or uid == "":
        data = dict(ok=0)
        return json.dumps(data)

    if (mid is None) or mid == "":
        data = dict(ok=0)
        return json.dumps(data)

    moviecol = Moviecol.query.filter(
        Moviecol.movie_id == int(mid),
        Moviecol.user_id == int(uid)
    ).count()

    if moviecol == 1:
        data = dict(ok=0)
    if moviecol == 0:
        moviecol = Moviecol(
            movie_id=mid,
            user_id=uid
        )
        db.session.add(moviecol)
        db.session.commit()
        data = dict(ok=1)

    return json.dumps(data)

@home.route("/search/<int:page>/", methods=['GET'])
def search(page=None):
    """
    电影搜索
    """
    if page is None:
        page = 1
    key = request.args.get("key", "")
    movie_count = Movie.query.filter(
        Movie.title.ilike("%" + key + "%")
    ).count()
    page_data = Movie.query.filter(
        Movie.title.ilike("%" + key + "%")
    ).paginate(page=page, per_page=8)
    page_data.key = key
    return render_template("home/search.html", key=key, movie_count=movie_count, page_data=page_data)


@home.route("/play/<int:id>/<int:page>/", methods=['GET', 'POST'])
def play(id=None,page=None):
    '''
    电影详情
    '''
    movie = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id,
        Movie.id == int(id)
    ).first_or_404()

    if page is None:
        page = 1

    page_data = Comment.query.join(Movie).join(User).filter(
        Comment.movie_id == movie.id,
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=8)

    movie.playnum = movie.playnum + 1

    form = CommentForm()
    if form.validate_on_submit():
        data = form.data
        comment = Comment(
            content=data['content'],
            movie_id=movie.id,
            user_id=session['user_id']
        )
        db.session.add(comment)
        db.session.commit()

        movie.commentnum = movie.commentnum + 1
        db.session.add(movie)
        db.session.commit()
        flash("评论添加成功!", category="ok")
        return redirect(url_for("home.play", id=movie.id, page=1))
    db.session.add(movie)
    db.session.commit()
    return render_template("home/play.html", form=form, movie=movie, page_data=page_data)
