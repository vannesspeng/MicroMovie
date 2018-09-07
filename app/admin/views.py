import os
import uuid
from datetime import datetime
from functools import wraps

from flask import render_template, redirect, url_for, request, flash, session
from werkzeug.utils import secure_filename

from app import db, app
from app.admin.forms import LoginForm, TagForm, MovieForm
from app.models import Admin, Tag, Movie
from . import admin

'''定义登录装饰器'''


def admin_log_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@admin.route('/')
@admin_log_req
def index():
    return render_template("admin/index.html")


@admin.route("/login/", methods=["POST", "GET"])
def login():
    """
    后台登录
    """
    from werkzeug.security import generate_password_hash
    temp = generate_password_hash('admin')
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data['account']).first()
        if not admin.check_pwd(data['pwd']):
            flash('密码错误')
            return redirect(url_for('admin.login'))
        session['admin'] = data['account']
        return redirect(request.args.get('next') or url_for('admin.index'))
    return render_template("admin/login.html", form=form)


@admin.route("/logout/")
@admin_log_req
def logout():
    """
    后台注销登录
    """
    return redirect(url_for("admin.login"))


@admin.route("/pwd/")
@admin_log_req
def pwd():
    """
    修改登录
    """
    return render_template("admin/pwd.html")


@admin.route("/tag/add", methods=['GET', 'POST'])
@admin_log_req
def tag_add():
    """
    标签添加与编辑
    """
    form = TagForm()
    data = form.data
    if form.validate_on_submit():
        # 判断标签是否存在
        tag = Tag.query.filter_by(name=data['name']).first()
        if tag:
            flash('标签已经存在', 'err')
            return redirect(url_for('admin.tag_add'))
        tag = Tag(
            name=data['name']
        )
        db.session.add(tag)
        db.session.commit()
        flash('标签添加成功', "ok")
        return redirect(url_for('admin.tag_add'))
    return render_template('admin/tag_add.html', form=form)


@admin.route("/tag/list/<int:page>/", methods=['GET'])
@admin_log_req
def tag_list(page=None):
    """
    标签列表
    """
    if page is None:
        page = 1
    page_data = Tag.query.order_by(
        Tag.addtime.desc()
    ).paginate(page=page, per_page=3)
    return render_template('admin/tag_list.html', page_data=page_data)


@admin.route("/tag/del/<int:id>/", methods=['GET'])
@admin_log_req
def tag_del(id=None):
    """
    标签删除
    """
    tag = Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash("标签<<{0}>>删除成功".format(tag.name), "ok")
    return redirect(url_for('admin.tag_list', page=1))


@admin.route("/tag/edit/<int:id>/", methods=["GET", "POST"])
@admin_log_req
def tag_edit(id=None):
    form = TagForm()
    form.submit.label.text = "修改"
    tag = Tag.query.get_or_404(id)
    if form.validate_on_submit():
        data = form.data
        tag_count = Tag.query.filter_by(name=data['name']).count()
        if tag_count == 1:
            flash('修改的标签名已经存在，请勿重复添加', category='err')
            return redirect(url_for('admin.tag_edit', id=id))
        tag.name = data['name']
        db.session.add(tag)
        db.session.commit()
        flash('标签修改成功', category='ok')
        return redirect(url_for('admin.tag_edit', id=id))
    return render_template("admin/tag_edit.html", form=form, tag=tag)


def change_filename(filename):
    file_info = os.path.splitext(filename)
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + file_info[-1]
    return filename


@admin.route("/movie/add/", methods=['POST', 'GET'])
@admin_log_req
def movie_add():
    """
    编辑电影页面
    """
    form = MovieForm()
    if form.validate_on_submit():
        data = form.data
        # 获取影片视频文件和封面图片文件
        file_url = secure_filename(form.url.data.filename)
        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config['UP_DIR']):
            os.makedirs(app.config['UP_DIR'])
            os.chmod(app.config['UP_DIR'], 'rw')
        # 文件上传
        url = change_filename(file_url)
        logo = change_filename(file_logo)
        form.url.data.save(app.config["UP_DIR"] + url)
        form.logo.data.save(app.config["UP_DIR"] + logo)
        movie = Movie(
            title=data['title'],
            url=url,
            info=data['info'],
            logo=logo,
            star=int(data['star']),
            playnum=0,
            commentnum=0,
            tag_id=int(data["tag_id"]),
            area=data["area"],
            release_time=data["release_time"],
            length=data["length"]
        )
        db.session.add(movie)
        db.session.commit()
        flash("添加电影<<{0}>>成功！".format(movie.title), "ok")
        return redirect(url_for('admin.movie_add'))
    return render_template("admin/movie_add.html", form=form)


@admin.route("/movie/del/<int:id>/", methods=['GET'])
@admin_log_req
def movie_del(id=None):
    """
    电影删除页面
    """
    movie = Movie.query.filter_by(id=id).first_or_404()
    db.session.delete(movie)
    db.session.commit()
    movie_file = app.config['UP_DIR'] + movie.url
    logo_file = app.config['UP_DIR'] + movie.logo
    flash('影片<<{0}>>删除成功'.format(movie.title), category='ok')
    # 判断文件是否存在
    if (os.path.exists(movie_file)):
        os.remove(movie_file)
    else:
        flash('影片视频文件不存在')

    if (os.path.exists(logo_file)):
        os.remove(logo_file)
    else:
        flash('影片logo文件不存在')
    return redirect(url_for('admin.movie_list', page=1))


@admin.route("/movie/list/<int:page>/", methods=['GET'])
@admin_log_req
def movie_list(page=None):
    """
    电影列表页面
    """
    if page == None:
        page = 1
    page_data = Movie.query.order_by(Movie.release_time.desc()).paginate(page=page, per_page=2)
    return render_template("admin/movie_list.html", page_data=page_data)


@admin.route("/movie/edit/<int:id>/", methods=['POST', 'GET'])
@admin_log_req
def movie_edit(id=None):
    """
    电影列表页面
    """
    form = MovieForm()
    form.url.validators = []
    form.logo.validators = []

    movie = Movie.query.get_or_404(int(id))
    # 赋初值
    if request.method == "GET":
        form.info.data = movie.info
        form.tag_id.data = movie.tag_id
        form.star.data = movie.star

    if form.validate_on_submit():
        data = form.data
        # 判断片名是否存在
        movie_count = Movie.query.filter_by(title=data['title']).count()

        if movie_count == 1 and movie.title == data['title']:
            flash('片名已经存在!', category='err')
            return redirect(url_for('admin.movie_edit', id=id))

        # 上传视频文件以及logo图片文件
        if not os.path.exists(app.config['UP_DIR']):
            os.makedirs(app.config['UP_DIR'])
            os.chmod(app.config['UP_DIR'], 'rw')

        # 视频文件上传
        if form.url.data.filename != None:
            # 先要删除原文件，再上传修改后的新文件
            old_movie_file = app.config['UP_DIR'] + movie.url
            if os.path.exists(old_movie_file):
                os.remove(old_movie_file)
            file_url = secure_filename(form.url.data.filename)
            movie.url = change_filename(file_url)
            form.url.data.save(app.config["UP_DIR"] + movie.url)


        # LOGO文件上传
        if form.logo.data.filename != None:
            logo_file = app.config['UP_DIR'] + movie.logo
            if os.path.exists(logo_file):
                os.remove(logo_file)
            file_logo = secure_filename(form.logo.data.filename)
            movie.logo = change_filename(file_logo)
            form.logo.data.save(app.config["UP_DIR"] + movie.logo)

        movie.star = data['star']
        movie.tag_id = data['tag_id']
        movie.info = data['info']
        movie.title = data['title']
        movie.area = data['area']
        movie.length = data['length']
        movie.release_time = data['release_time']
        db.session.add(movie)
        db.session.commit()
        flash("电影修改成功!", category="ok")
        return redirect(url_for('admin.movie_edit', id=id))
    return render_template("admin/movie_edit.html", form=form, movie=movie)


@admin.route("/preview/add/")
@admin_log_req
def preview_add():
    """
    上映预告添加
    """
    return render_template("admin/preview_add.html")


@admin.route("/preview/list/")
@admin_log_req
def preview_list():
    """
    上映预告列表
    """
    return render_template("admin/preview_list.html")


@admin.route("/user/list/")
@admin_log_req
def user_list():
    """
    会员列表
    """
    return render_template("admin/user_list.html")


@admin.route("/user/view/")
@admin_log_req
def user_view():
    """
    查看会员
    """
    return render_template("admin/user_view.html")


@admin.route("/comment/list/")
@admin_log_req
def comment_list():
    """
    评论列表
    """
    return render_template("admin/comment_list.html")


@admin.route("/moviecol/list/")
@admin_log_req
def moviecol_list():
    """
    电影收藏
    """
    return render_template("admin/moviecol_list.html")


@admin.route("/oplog/list/")
@admin_log_req
def oplog_list():
    """
    操作日志管理
    """
    return render_template("admin/oplog_list.html")


@admin.route("/adminloginlog/list/")
@admin_log_req
def adminloginlog_list():
    """
    管理员日志列表
    """
    return render_template("admin/adminloginlog_list.html")


@admin.route("/userloginlog/list/")
@admin_log_req
def userloginlog_list():
    """
    会员日志列表
    """
    return render_template("admin/userloginlog_list.html")


@admin.route("/auth/add/")
@admin_log_req
def auth_add():
    """
    添加权限
    """
    return render_template("admin/auth_add.html")


@admin.route("/auth/list/")
@admin_log_req
def auth_list():
    """
    权限列表
    """
    return render_template("admin/auth_list.html")


@admin.route("/role/add/")
@admin_log_req
def role_add():
    """
    添加角色
    """
    return render_template("admin/role_add.html")


@admin.route("/role/list/")
@admin_log_req
def role_list():
    """
    角色列表
    """
    return render_template("admin/role_list.html")


@admin.route("/admin/add/", methods=['GET', 'POST'])
@admin_log_req
def admin_add():
    """
    添加管理员
    """
    return render_template("admin/admin_add.html")


@admin.route("/admin/list/")
@admin_log_req
def admin_list():
    """
    管理员列表
    """
    return render_template("admin/admin_list.html")
