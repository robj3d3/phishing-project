from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user
from app.auth import bp
from app.auth.forms import AdminLoginForm, AdminRegistrationForm
from app.models import Admin
from app import db

from urllib.parse import urlparse, urljoin

# http://flask.pocoo.org/snippets/62/
# security measure to ensure redirect is to a URL in the same server as the host - preventing external redirects
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    no_account = False # need to pass Boolean to Jinja for rendering
    if len(list(Admin.query.all())) == 0:
        no_account = True
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid login credentials.')
            return redirect(url_for('auth.login'))
        login_user(user, force=True)
        next_page = request.args.get('next')
        if not is_safe_url(next_page):
            return flask.abort(400)
        return redirect(next_page or url_for('main.index'))
    return render_template('auth/login.html', title='Admin Sign In', form=form, no_account=no_account)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated or len(list(Admin.query.all())) > 0:
        flash('Admin account already exists.')
        return redirect(url_for('main.index'))
    form = AdminRegistrationForm()
    if form.validate_on_submit():
        admin = Admin(username=form.username.data)
        admin.set_password(form.password.data)
        db.session.add(admin)
        db.session.commit()
        flash('Admin account registered.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register Admin Account', form=form)