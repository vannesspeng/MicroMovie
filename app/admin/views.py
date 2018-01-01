import os
import uuid
from datetime import datetime
from functools import wraps

from flask import render_template, redirect, url_for, request, flash, session, abort
from werkzeug.utils import secure_filename

from app import db, app
from app.admin.forms import LoginForm, TagForm, MovieForm, PreviewForm, PwdForm, AuthForm, RoleForm, AdminForm
from app.models import Admin, Tag, Movie, Preview, User, Comment, Moviecol, Oplog, Adminlog, Userlog, Auth, Role
from . import admin

'''定义登录装饰器'''


def admin_log_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


'''定义权限控制装饰器'''


def admin_auth(f):
    # 权限查询
    @wraps(f)
    def decorator_function(*args, **kwargs):
        # 查询session里的admin，通过admin的角色，来查询该角色所能访问的url
        admin = Admin.query.join(
            Role
        ).filter(
            Role.id == Admin.role_id,
            Admin.id == session['admin_id']
        ).first()
        if admin:
            auths = admin.role.auths
            auths = list(map(lambda v: int(v), auths.split(",")))
            auth_list = Auth.query.all()
            urls = [v.url for v in auth_list for val in auths if val == v.id]
            rule = request.url_rule
            if str(rule) not in urls:
                abort(404)
        return f(*args, **kwargs)

    return decorator_function


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
            flash('密码错误', category='err')
            return redirect(url_for('admin.login'))
        session['admin'] = data['account']
        session['admin_id'] = admin.id
        adminlog = Adminlog(
            admin_id=admin.id,
            ip=request.remote_addr
        )
        db.session.add(adminlog)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('admin.index'))
    return render_template("admin/login.html", form=form)


@admin.route("/logout/")
@admin_log_req
def logout():
    """
    后台注销登录
    """
    session.pop('admin')
    session.pop('admin_id')
    return redirect(url_for("admin.login"))


@admin.route("/pwd/", methods=['GET', 'POST'])
@admin_log_req
def pwd():
    """
    修改密码
    """
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        # 验证老密码的正确性
        admin = Admin.query.filter_by(name=session['admin']).first()
        if data['old_pwd'] == data['new_pwd']:
            flash('密码修改失败，新密码与老密码相同，请重新输入新密码！', category='err')
            return redirect(url_for("admin.pwd"))
        else:
            from werkzeug.security import generate_password_hash
            admin.pwd = generate_password_hash(data['new_pwd'])
            db.session.add(admin)
            db.session.commit()
            flash('密码修改成功，重新登陆', category='ok')
            return redirect(url_for("admin.logout"))
    return render_template("admin/pwd.html", form=form)


@admin.route("/tag/add", methods=['GET', 'POST'])
@admin_log_req
@admin_auth
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
        oplog = Oplog(
            admin_id=session['admin_id'],
            ip=request.remote_addr,
            reason="添加标签%s" % data["name"]
        )
        db.session.add(oplog)
        db.session.commit()
        flash('标签添加成功', "ok")
        return redirect(url_for('admin.tag_add'))
    return render_template('admin/tag_add.html', form=form)


@admin.route("/tag/list/<int:page>/", methods=['GET'])
@admin_log_req
@admin_auth
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

        if movie_count == 1 and movie.title != data['title']:
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


@admin.route("/preview/add/", methods=["GET", "POST"])
@admin_log_req
def preview_add():
    """
    上映预告添加
    """
    form = PreviewForm()
    if request.method == 'GET':
        form.submit.label.label = '添加'

    if form.validate_on_submit():
        data = form.data
        # 保存标题图片
        if not os.path.exists(app.config['UP_DIR']):
            os.mkdirs(app.config['UP_DIR'])
            os.chmod(app.config['UP_DIR'], 'rw')

        if form.logo.data.filename != None:
            file_logo = secure_filename(form.logo.data.filename)
            logo = change_filename(file_logo)
            form.logo.data.save(app.config['UP_DIR'] + logo)
            preview = Preview(
                title=data['title'],
                logo=logo
            )
            db.session.add(preview)
            db.session.commit()
            flash('封面logo添加成功', category='ok')
            return redirect(url_for("admin.preview_add"))
    return render_template("admin/preview_add.html", form=form)


@admin.route("/preview/list/<int:page>/", methods=['POST', 'GET'])
@admin_log_req
def preview_list(page=None):
    """
    上映预告列表
    """
    if page is None:
        page = 1
    page_data = Preview.query.order_by(Preview.addtime.desc()).paginate(page=page, per_page=3)
    return render_template("admin/preview_list.html", page_data=page_data)


@admin.route("/preview/del/<int:id>/", methods=["GET"])
@admin_log_req
def preview_del(id=None):
    preview = Preview.query.get_or_404(id)
    preview_img = app.config['UP_DIR'] + preview.logo
    if os.path.exists(preview_img):
        os.remove(preview_img)
    db.session.delete(preview)
    db.session.commit()
    flash("标题<<{0}>>删除成功".format(preview.title), category='ok')
    return redirect(url_for("admin.preview_list", page=1))


@admin.route("/preview/edit/<int:id>/", methods=["GET", "POST"])
@admin_log_req
def preview_edit(id=None):
    """
    上映预告添加
    """
    form = PreviewForm()
    preview = Preview.query.get_or_404(int(id))
    if form.validate_on_submit():
        data = form.data
        # 保存标题图片
        if not os.path.exists(app.config['UP_DIR']):
            os.mkdirs(app.config['UP_DIR'])
            os.chmod(app.config['UP_DIR'], 'rw')

        if form.logo.data.filename != None:
            file_logo = secure_filename(form.logo.data.filename)
            logo = change_filename(file_logo)
            form.logo.data.save(app.config['UP_DIR'] + logo)
            preview.title = data['title']
            db.session.add(preview)
            db.session.commit()
            flash('封面logo更新成功', category='ok')
            return redirect(url_for("admin.preview_edit", id=id))
    return render_template("admin/preview_edit.html", form=form, preview=preview)


@admin.route("/user/list/<int:page>/", methods=["GET", "POST"])
@admin_log_req
def user_list(page=None):
    """
    会员列表
    """
    if page is None:
        page = 1
    page_data = User.query.order_by(User.addtime).paginate(page=page, per_page=4)
    return render_template("admin/user_list.html", page_data=page_data)


@admin.route("/user/view/<int:id>/", methods=['GET', 'POST'])
@admin_log_req
def user_view(id=None):
    """
    查看会员
    """
    from_page = request.args.get('fp')
    user = User.query.get_or_404(int(id))
    return render_template("admin/user_view.html", user=user, from_page=from_page)


@admin.route('/user/del/<int:id>/')
@admin_log_req
def user_del(id=None):
    from_page = int(request.args.get('fp')) - 1
    if not from_page:
        from_page = 1
    user = User.query.get_or_404(int(id))
    db.session.delete(user)
    db.session.commit()
    flash('会员删除成功!', category='ok')
    return redirect(url_for('admin.user_list', page=from_page))


@admin.route("/comment/list/<int:page>/", methods=['GET'])
@admin_log_req
def comment_list(page=None):
    """
    评论列表
    """
    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=4)
    return render_template("admin/comment_list.html", page_data=page_data)


@admin.route("/comments/del/<int:id>/", methods=['GET'])
@admin_log_req
def comment_del(id=None):
    from_page = int(request.args.get('fp')) - 1
    if not from_page:
        from_page = 1
    comment = Comment.query.get_or_404(int(id))
    db.session.delete(comment)
    db.session.commit()
    flash('评论删除成功!', category='ok')
    return redirect(url_for('admin.comment_list', page=from_page))


@admin.route("/moviecol/list/<int:page>/", methods=['GET'])
@admin_log_req
def moviecol_list(page=None):
    """
    电影收藏
    """
    if page is None:
        page = 1
    page_data = Moviecol.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Moviecol.movie_id,
        User.id == Moviecol.user_id
    ).order_by(
        Moviecol.addtime.desc()
    ).paginate(page=page, per_page=4)
    return render_template("admin/moviecol_list.html", page_data=page_data)


@admin.route('/moviecol/del/<int:id>/', methods=['GET'])
@admin_log_req
def moviecol_del(id=None):
    from_page = int(request.args.get('fp')) - 1
    if not from_page:
        from_page = 1
    moviecol = Moviecol.query.get_or_404(int(id))
    db.session.delete(moviecol)
    db.session.commit()
    flash('收藏删除成功!', category='ok')
    return redirect(url_for('admin.moviecol_list', page=from_page))


@admin.route("/oplog/list/<int:page>/", methods=['GET'])
@admin_log_req
def oplog_list(page=None):
    """
    操作日志管理
    """
    if page is None:
        page = 1
    page_data = Oplog.query.join(
        Admin
    ).filter(
        Admin.id == Oplog.admin_id
    ).order_by(
        Oplog.addtime.desc()
    ).paginate(page=page, per_page=8)
    return render_template("admin/oplog_list.html", page_data=page_data)


@admin.route("/adminloginlog/list/<int:page>", methods=['GET'])
@admin_log_req
def adminloginlog_list(page=None):
    """
    管理员日志列表
    """
    if page is None:
        page = 1
    page_data = Adminlog.query.join(
        Admin
    ).filter(
        Admin.id == Adminlog.admin_id
    ).order_by(
        Adminlog.addtime.desc()
    ).paginate(page=page, per_page=8)
    return render_template("admin/adminloginlog_list.html", page_data=page_data)


@admin.route("/userloginlog/list/<int:page>/")
@admin_log_req
def userloginlog_list(page=None):
    """
    会员日志列表
    """
    if page is None:
        page = 1
    page_data = Userlog.query.join(
        User
    ).filter(
        User.id == Userlog.user_id
    ).order_by(
        Userlog.addtime.desc()
    ).paginate(page=page, per_page=6)
    return render_template("admin/userloginlog_list.html", page_data=page_data)


@admin.route("/auth/add/", methods=['GET', 'POST'])
@admin_log_req
def auth_add():
    """
    添加权限
    """
    form = AuthForm()
    if request.method == 'GET':
        form.submit.label.text = '添加'

    if form.validate_on_submit():
        data = form.data
        auth = Auth(
            name=data['name'],
            url=data['url']
        )
        db.session.add(auth)
        db.session.commit()
        flash('权限添加成功', category='ok')
        return redirect(url_for('admin.auth_add'))
    return render_template("admin/auth_add.html", form=form)


@admin.route("/auth/list/<int:page>/", methods=['GET'])
@admin_log_req
def auth_list(page=None):
    """
    权限列表
    """
    if page is None:
        page = 1
    page_data = Auth.query.order_by(Auth.addtime.desc()).paginate(page=page, per_page=2)
    return render_template("admin/auth_list.html", page_data=page_data)


@admin.route("/auth/del/<int:id>/", methods=['GET'])
@admin_log_req
def auth_del(id=None):
    """
    删除权限
    """
    now_page = request.args.get('now_page')
    page_data_has_next = request.args.get('page_data_has_next')
    page_data_items_length = request.args.get('page_data_items_length')
    if (not page_data_has_next) and page_data_items_length == 1:
        page = now_page - 1
    else:
        page = now_page
    auth = Auth.query.get_or_404(int(id))
    db.session.delete(auth)
    db.session.commit()
    flash('权限删除成功', category='ok')
    return redirect(url_for("admin.auth_list", page=page))


@admin.route("/auth/edit/<int:id>", methods=['GET', 'POST'])
@admin_log_req
def auth_edit(id=None):
    """
    编辑权限
    """
    form = AuthForm()
    auth = Auth.query.get_or_404(int(id))
    if form.validate_on_submit():
        data = form.data
        auth.name = data['name']
        auth.url = data['url']
        db.session.add(auth)
        db.session.commit()
        flash('权限信息修改成功', category='ok')
        return redirect(url_for('admin.auth_edit', id=auth.id))
    return render_template("admin/auth_edit.html", form=form, auth=auth)


@admin.route("/role/add/", methods=['GET', 'POST'])
@admin_log_req
def role_add():
    """
    添加角色
    """
    form = RoleForm()
    if request.method == 'GET':
        form.submit.label.text = '添加'

    if form.validate_on_submit():
        data = form.data
        role = Role(
            name=data['name'],
            auths=",".join(map(lambda v: str(v), data['auths']))
        )
        db.session.add(role)
        db.session.commit()
        flash('角色添加成功！', category='ok')
        return redirect(url_for('admin.role_add'))
    return render_template("admin/role_add.html", form=form)


@admin.route("/role/list/<int:page>/", methods=['GET'])
@admin_log_req
def role_list(page=None):
    """
    角色列表
    """
    if page is None:
        page = 1
    page_data = Role.query.order_by(Role.addtime.desc()).paginate(page=page, per_page=8)
    return render_template("admin/role_list.html", page_data=page_data)


@admin.route("/role/del/<int:id>/", methods=['GET'])
@admin_log_req
def role_del(id=None):
    """
    角色列表
    """
    role = Role.query.get_or_404(int(id))
    db.session.delete(role)
    db.session.commit()
    flash('角色删除成功!', category='ok')
    return redirect(url_for('admin.role_list', page=1))


@admin.route("/role/edit/<int:id>/", methods=['GET', 'POST'])
@admin_log_req
def role_edit(id=None):
    """
    添加角色
    """
    form = RoleForm()
    role = Role.query.get_or_404(int(id))
    if request.method == "GET":
        auths = role.auths
        form.auths.data = list(map(lambda v: int(v), auths.split(",")))

    if form.validate_on_submit():
        data = form.data
        role = Role(
            name=data['name'],
            auths=",".join(map(lambda v: str(v), data['auths']))
        )
        db.session.add(role)
        db.session.commit()
        flash('角色修改成功！', category='ok')
        return redirect(url_for('admin.role_add'))
    return render_template("admin/role_edit.html", form=form, role=role)


@admin.route("/admin/add/", methods=['GET', 'POST'])
@admin_log_req
def admin_add():
    """
    添加管理员
    """
    form = AdminForm()
    if form.validate_on_submit():
        from werkzeug.security import generate_password_hash
        data = form.data
        admin = Admin(
            name=data['name'],
            pwd=generate_password_hash(data['pwd']),
            role_id=data['role_id'],
            is_super=1
        )
        db.session.add(admin)
        db.session.commit()
        flash('管理员添加成功', category='ok')
        return redirect(url_for('admin.admin_add'))
    return render_template("admin/admin_add.html", form=form)


@admin.route("/admin/list/<int:page>/", methods=['GET'])
@admin_log_req
def admin_list(page=None):
    """
    管理员列表
    """
    if page is None:
        page = 1
    page_data = Admin.query.join(
        Role
    ).filter(
        Role.id == Admin.role_id
    ).order_by(
        Admin.addtime.desc()
    ).paginate(page=page, per_page=8)
    return render_template("admin/admin_list.html", page_data=page_data)
