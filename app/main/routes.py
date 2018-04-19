from flask import render_template, redirect, url_for, flash
from app import db
from app.main.forms import UserForm
from app.models import User
from app.main import bp

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', title='Home')

@bp.route('/addusers', methods=['GET', 'POST'])
def addusers():
    form = UserForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        flash('New user added!')
        return redirect(url_for('main.addusers'))
    return render_template('main/addusers.html', title='Add Users', form=form)