from flask import render_template, redirect, url_for, flash
from app import db
from app.main.forms import StaffForm
from app.models import Staff
from app.main import bp

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', title='Home')

@bp.route('/control', methods=['GET', 'POST'])
def control():
    form = StaffForm()
    if form.validate_on_submit():
        staff = Staff(staffname=form.staffname.data, email=form.email.data)
        db.session.add(staff)
        db.session.commit()
        flash('New staff added!')
        return redirect(url_for('main.control'))
    return render_template('main/control.html', title='Control Panel', form=form)