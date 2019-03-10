from flask import render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_required
from app.reports import bp
from app.reports.forms import SearchStaffForm, SearchDepartmentForm, SearchRiskScoreForm
from app.models import Staff, Departments
from sqlalchemy import func

@bp.before_app_request
def before_request():
    session.permanent = True # Sets session lifetime to value stored in config variable (5 minutes).


@bp.route('/reports', methods=['GET', 'POST']) # Decorator registers the /reports route with the reports() view function, accepting only GET and POST requests to the page. This page is used by the system administrator to
                                               # query the database and return a paginated list of staff members with a specific risk score or greater.
@login_required # Decorator ensures current user is logged in and authenticated before loading the reports() view. If the user is not authenticated, they will be redirected to the login() view function in the 'auth' directory.
def reports():
    form = SearchRiskScoreForm() # Instantiates an object of the SearchRiskScoreForm class. This form is used to query the Staff table of the database and return Staff records with a given risk score or higher.
    if form.validate_on_submit(): # Executes following sequence if it is a POST request (i.e. form submission) and it is validated.
        page = request.args.get('page', 1, type=int) # Implements page number as a query string argument called 'page' in the page's URL, default page is 1 and the page number data type is integer.
        staff = Staff.query.filter(Staff.risk_score>=form.risk_score.data).order_by(Staff.risk_score.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False) # Returns pagination object for the corresponding page number which contains POSTS_PER_PAGE (assigned in 'config.py') number of desired records of the Staff table, ordered by descending risk_score,
                                                                                                                                                                         # containing records only with a risk_score greater than or equal to the value submitted in the form by the user. The False argument returns an empty page instead of HTTP status code 404 (Not Found) for a non-existing page.
        if staff.has_next: # staff.has_next returns True if there is at least one more page after the current page
            next_url = url_for('reports.reports', page=staff.next_num) # Sets next_url to URL for the next page, with the page number for the next page retrieved from staff.next_num
        else:
            next_url = None
        if staff.has_prev: # staff.has_prev returns True if there is at least one more page before the current page
            prev_url = url_for('reports.reports', page=staff.prev_num) # Sets prev_url to URL for the previous page, with the page number for the previous page retrieved from staff.prev_num
        else:
            prev_url = None
        return render_template('reports/reports.html', title='Reports', form=form, staff=staff.items, next_url=next_url, prev_url=prev_url) # Renders the template 'reports.html' located in the 'reports' directory of templates, with page title 'Reports', and passing the form object, staff.items (list of items in the requested page),
                                                                                                                                            # URL for the next page of results, and the URL for the previous page of results.
    else: # If the page has been accessed as a GET request, the following sequence will execute, loading a paginated list of all Staff records in order of descending risk_score, such that those with the highest risk score are seen at the top of the list.
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
        return render_template('reports/reports.html', title='Reports', form=form, staff=staff.items, next_url=next_url, prev_url=prev_url)

@bp.route('/reports/staff', methods=['GET', 'POST']) # This page is used by the system administrator to search for a specific Staff record (or records) by staff name.
@login_required
def reports_staff():
    form = SearchStaffForm() # Instantiates an object of the SearchStaffForm class. This form is used to query the Staff table of the database and return the Staff record(s) with the staff_name field containing the staff name provided in the submitted form object. 
    if form.validate_on_submit(): # Executes the following sequence if the form is submitted with a POST request and the data submitted is validated.
        page = request.args.get('page', 1, type=int)
        staff = Staff.query.filter( # Returns pagination object containing a list of Staff records queried from the Staff table in the database (ordered by descending risk score), where the queried record staff_name fields contain the staff name provided in the submitted
            func.lower(Staff.staff_name).contains(func.lower(form.staff_name.data)) # form object as a substring, i.e. if the staff_name 'John' was submitted in the search form, any Staff records which have 'John' as a substring of the staff_name field would be returned,
            ).order_by(Staff.risk_score.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False) # e.g. 'John Smith', 'Steve Johnson' and 'Johnny Parker' would all be returned as they all contain the substring 'John'. The search is not case sensitive, as both
                                                                                                            # the staff_name field of the Staff record and the submitted staff name are set to lower case using the function func.lower() prior to comparison.
        if staff.has_next:
            next_url = url_for('reports.reports_staff', page=staff.next_num)
        else:
            next_url = None
        if staff.has_prev:
            prev_url = url_for('reports.reports_staff', page=staff.prev_num)
        else:
            prev_url = None
        return render_template('reports/reports_staff.html', title='Search Staff', form=form, staff=staff.items, next_url=next_url, prev_url=prev_url)
    else:
        return render_template('reports/reports_staff.html', title='Search Staff', form=form) # If the page has been accessed as a GET request, i.e. the form has not been submitted, no paginated list will be displayed by default. Instead, the page will be empty excluding the form.

@bp.route('/reports/departments', methods=['GET', 'POST']) # This page is used by the system administrator to search for a specific Departments record by department name from a dynamic drop-down list.
@login_required
def reports_departments():
    form = SearchDepartmentForm() # Instantiates an object of the SearchDepartmentForm class. This form is used to query the Departments table of the database and return the staff records that are related to the queried Department record, as well as the average department risk score.
    form.department.choices = [(i.id, i.department_name) for i in Departments.query.order_by('department_name')] # Choices list assigned after form instantiation to create a dynamic drop-down list. Consists of all department names stored in Departments table records.
    if form.validate_on_submit(): # Executes the following sequence if the form is submitted with a POST request and the data submitted is validated.
        department = Departments.query.get(form.department.data) # Queries the Departments table of the database, returning the Departments record indexed by the selected department's id.
        page = request.args.get('page', 1, type=int)
        staff = Staff.query.filter(Staff.department_id==form.department.data).order_by(Staff.risk_score.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False) # Returns pagination object containing a list of Staff records queried from the Staff table in the database (ordered by descending risk score),
                                                                                                                                                                            # where the Staff records have the foreign key department_id field equal to the id provided in the submitted form object.
        if staff.has_next:
            next_url = url_for('reports.reports_departments', page=staff.next_num)
        else:
            next_url = None
        if staff.has_prev:
            prev_url = url_for('reports.reports_departments', page=staff.prev_num)
        else:
            prev_url = None
        return render_template('reports/reports_departments.html', title='Search Department', form=form, department=department, staff=staff.items, next_url=next_url, prev_url=prev_url)
    else:
        return render_template('reports/reports_departments.html', title='Search Department', form=form) # If the page has been accessed as a GET request, i.e. the form has not been submitted, no paginated list will be displayed by default. Instead, the page will be empty excluding the form.

    # POST/REDIRECT/GET pattern (shown below) does not work! Redirect will result in paginated object being re-generated, making form useless.

    # form = SearchDepartmentForm()
    # form.department.choices = [(i.id, i.department_name) for i in Departments.query.order_by('department_name')]
    # page = request.args.get('page', 1, type=int)
    # staff = Staff.query.order_by(Staff.staff_name).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    # department = None
    # if staff.has_next:
    #     next_url = url_for('reports.reports_departments', page=staff.next_num)
    # else:
    #     next_url = None
    # if staff.has_prev:
    #     prev_url = url_for('reports.reports_departments', page=staff.prev_num)
    # else:
    #     prev_url = None
    # if form.validate_on_submit():
    #     department = Departments.query.get(form.department.data)
    #     page = request.args.get('page', 1, type=int)
    #     staff = Staff.query.filter(Staff.department_id==form.department.data).order_by(Staff.risk_score.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    #     if staff.has_next:
    #         next_url = url_for('reports.reports_departments', page=staff.next_num)
    #     else:
    #         next_url = None
    #     if staff.has_prev:
    #         prev_url = url_for('reports.reports_departments', page=staff.prev_num)
    #     else:
    #         prev_url = None
    #     return redirect(url_for('reports.reports_departments'))
    # return render_template('reports/reports_departments.html', title='Search Department', form=form, department=department, staff=staff.items, next_url=next_url, prev_url=prev_url)
