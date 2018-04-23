from flask import render_template, redirect, url_for, flash, request, current_app
from app import db
from app.main.forms import StaffForm, SendEmail
from app.models import Staff
from app.main import bp
from app.main.email import send_phishing_email

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    form = StaffForm()
    if form.validate_on_submit():
        staff = Staff(staffname=form.staffname.data, email=form.email.data)
        db.session.add(staff)
        db.session.commit()
        flash('New staff added!')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    staff = Staff.query.order_by(Staff.staffname).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    if staff.has_next:
        next_url = url_for('main.index', page=staff.next_num)
    else:
        next_url = None
    if staff.has_prev:
        prev_url = url_for('main.index', page=staff.prev_num)
    else:
        prev_url = None
    return render_template('index.html', title='Dashboard', form=form, staff=staff.items, next_url=next_url, prev_url=prev_url)
    # items is attribute of object containing the list of items in requested page
    # False returns empty page instead of 404 for a non-existing page

@bp.route('/staff/<staffid>', methods=['GET', 'POST'])
def staff(staffid):
    form = SendEmail()
    if form.validate_on_submit():
        staff = Staff.query.filter_by(id=staffid).first()
        send_phishing_email(staff)
        flash('Phishing email sent, awaiting responses')
        return redirect(url_for('main.staff', staffid=staff.id))
    staff = Staff.query.filter_by(id=staffid).first_or_404()
    return render_template('staff.html', staff=staff, form=form)

# remember to provide POST method when incorporating a form
@bp.route('/fakepage1/<staffid>')
def fakepage1(staffid):
    staff = Staff.query.filter_by(id=staffid).first()
    flash('Staff member has clicked on this link!')
    return render_template('landingpages/fakepage1.html', staff=staff)