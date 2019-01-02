from flask import render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_required
from app.reports import bp
from app.reports.forms import SearchStaffForm, SearchDepartmentForm
from app.models import Staff, Departments
from sqlalchemy import func

@bp.before_app_request
def before_request():
    session.permanent = True # lifetime length in config


@bp.route('/reports', methods=['GET'])
@login_required
def reports():
    page = request.args.get('page', 1, type=int)
    staff = Staff.query.order_by(Staff.risk_score.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    if staff.has_next:
        next_url = url_for('reports.reports', page=staff.next_num)
    else:
        next_url = None
    if staff.has_prev:
        prev_url = url_for('reports.reports', page=staff.prev_num)
    else:
        prev_url = None
    return render_template('reports/reports.html', title='Reports', staff=staff.items, next_url=next_url, prev_url=prev_url)

@bp.route('/reports/staff', methods=['GET', 'POST'])
@login_required
def reports_staff():
    form = SearchStaffForm()
    if request.method == "GET":
        return render_template('reports/reports_staff.html', title='Search Staff', form=form)
    if form.validate_on_submit():
        page = request.args.get('page', 1, type=int)
        staff = Staff.query.filter(func.lower(Staff.staff_name)==func.lower(form.staff_name.data)).order_by(Staff.risk_score.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
        if staff.has_next:
            next_url = url_for('reports.reports_staff', page=staff.next_num)
        else:
            next_url = None
        if staff.has_prev:
            prev_url = url_for('reports.reports_staff', page=staff.prev_num)
        else:
            prev_url = None
        return render_template('reports/reports_staff.html', title='Search Staff', form=form, staff=staff.items, next_url=next_url, prev_url=prev_url)

@bp.route('/reports/departments', methods=['GET', 'POST'])
@login_required
def reports_departments():
    form = SearchDepartmentForm()
    form.department.choices = [(i.id, i.department_name) for i in Departments.query.order_by('department_name')]
    if request.method == "GET":
        return render_template('reports/reports_departments.html', title='Search Department', form=form)
    if form.validate_on_submit():
        department = Departments.query.get(form.department.data)
        page = request.args.get('page', 1, type=int)
        staff = Staff.query.filter(Staff.department_id==form.department.data).order_by(Staff.risk_score.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
        if staff.has_next:
            next_url = url_for('reports.reports_departments', page=staff.next_num)
        else:
            next_url = None
        if staff.has_prev:
            prev_url = url_for('reports.reports_departments', page=staff.prev_num)
        else:
            prev_url = None
        return render_template('reports/reports_departments.html', title='Search Department', form=form, department=department, staff=staff.items, next_url=next_url, prev_url=prev_url)