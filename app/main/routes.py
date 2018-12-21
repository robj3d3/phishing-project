from flask import render_template, redirect, url_for, flash, request, current_app
from app import db
from app.main.forms import StaffForm, SendEmail, LandingPage, RemoveStaffForm, EditStaffForm, ResetRiskScoreForm
from app.models import Staff, Departments
from app.main import bp
from app.main.email import send_phishing_email

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    form = StaffForm()
    form.department.choices = [(i.id, i.department_name) for i in Departments.query.order_by('department_name')]
    if form.validate_on_submit():
        staff = Staff(staff_name=form.staff_name.data, email=form.email.data, department_id=form.department.data)
        db.session.add(staff)
        db.session.commit()
        flash('New staff added!')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    staff = Staff.query.order_by(Staff.staff_name).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
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
    sendEmailForm = SendEmail()
    removeStaffForm = RemoveStaffForm()
    if sendEmailForm.validate_on_submit():
        staff = Staff.query.filter_by(id=staffid).first()
        email = sendEmailForm.selection.data
        send_phishing_email(staff, email) # where 'email' is the TEMPLATE name # there is threading so no need to queue
        flash('Phishing email sent, awaiting responses')
        return redirect(url_for('main.staff', staffid=staff.id))
    if removeStaffForm.validate_on_submit():
        staff = Staff.query.filter_by(id=staffid).first()
        db.session.delete(staff)
        db.session.commit()
        return redirect(url_for('main.index'))
    staff = Staff.query.filter_by(id=staffid).first_or_404()
    return render_template('staff.html', title='Staff Profile', staff=staff, department=Departments.query.get(staff.department_id), send_form=sendEmailForm, remove_form=removeStaffForm)

# remember to provide POST method when incorporating a form
@bp.route('/<page>/<staffid>', methods=['GET', 'POST'])
def landingpage(page, staffid):
    form = LandingPage()
    if request.method == "GET":
        staff = Staff.query.filter_by(id=staffid).first()
        staff.clicked += 1
        db.session.commit() # remember to commit!
    if request.method == "POST":
        staff = Staff.query.filter_by(id=staffid).first()
        staff.submitted += 1
        db.session.commit()
        return redirect(("https://www.{}.com/").format(page)) # means name MUST belong to URL - flexibility restriction
    return render_template(('landingpages/{}.html').format(page), title='Landing Page', staff=staff, form=form)


@bp.route('/staff/<staffid>/edit', methods=['GET', 'POST'])
def edit_staff(staffid):
    editStaffForm = EditStaffForm()
    resetRiskForm = ResetRiskScoreForm()
    editStaffForm.department.choices = [(i.id, i.department_name) for i in Departments.query.order_by('department_name')]
    if editStaffForm.validate_on_submit():
        staff = Staff.query.filter_by(id=staffid).first()
        staff.staff_name = editStaffForm.staff_name.data
        staff.email = editStaffForm.email.data
        staff.department_id = editStaffForm.department.data
        staff.risk_score = editStaffForm.risk_score.data
        db.session.commit()
        flash('Staff details have been updated.')
        return redirect(url_for('main.edit_staff', staffid=staff.id))
    if resetRiskForm.validate_on_submit():
        staff = Staff.query.filter_by(id=staffid).first()
        staff.risk_score = 0
        staff.delivered = 0
        staff.clicked = 0
        staff.submitted = 0
        db.session.commit()
        editStaffForm.staff_name.data = staff.staff_name
        editStaffForm.email.data = staff.email
        editStaffForm.department.data = staff.department_id
        editStaffForm.risk_score.data = staff.risk_score
    elif request.method == 'GET': # this will show the default for a GET request as the form filled with existing staff details
        staff = Staff.query.filter_by(id=staffid).first()
        editStaffForm.staff_name.data = staff.staff_name
        editStaffForm.email.data = staff.email
        editStaffForm.department.data = staff.department_id
        editStaffForm.risk_score.data = staff.risk_score
    staff = Staff.query.filter_by(id=staffid).first_or_404()
    return render_template('edit_staff.html', title='Edit Staff Profile', staff=staff, department=Departments.query.get(staff.department_id), edit_form=editStaffForm, reset_form=resetRiskForm)
