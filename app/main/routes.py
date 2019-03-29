from flask import render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_required
from app import db
from app.main.forms import StaffForm, SendEmail, ScheduleEmail, LandingPage, RemoveStaffForm, EditStaffForm, ResetRiskScoreForm
from app.models import Staff, Departments, ScheduledEmails
from app.main import bp
from app.main.email import send_phishing_email
import datetime

def recalculate_dep_risk(department): # Re-calculates a target department's average risk score (department object passed as argument).
    dep_risk = 0
    for i in list(department.staff_members): # Sums the risk scores of all staff members in the target department.
        dep_risk += i.risk_score
    if len(list(department.staff_members)) > 0: # Will execute provided there is at least one staff member still in the department.
        dep_risk /= len(list(department.staff_members)) # Calculates and assigns new average department risk score, by dividing sum of risk scores by the number of staff members in the department.
        department.risk_score = dep_risk
    else: # Will execute if there are no longer any staff members in the department, therefore new department risk score should be 0. This could be in the case of a staff member being removed from the database.
        department.risk_score = 0

@bp.before_app_request # Decorator registers a function that runs before the view function.
def before_request(): # Function runs before every view function, causing session timer to reset to 5 minutes. If user is idle for 5 minutes, they will be automatically logged out.
    session.permanent = True # Session lifetime stored in config (5 minutes). Default permanent session lifetime is 31 days.

@bp.route('/', methods=['GET', 'POST']) # Decorators register the / and /index routes with the index() view function, accepting only GET and POST requests to the page. This page acts as the application dashboard,
@bp.route('/index', methods=['GET', 'POST']) # with functionality to add new staff members to the database and view a list of existing staff members.
@login_required # Decorator ensures current user is logged in and authenticated before loading the index() view. If the user is not authenticated, they will be redirected to the login() view function in the 'auth' directory.
def index():
    form = StaffForm() # Instantiates an object of the StaffForm class. This form is used to add a new staff member record to the database.
    form.department.choices = [(i.id, i.department_name) for i in Departments.query.order_by('department_name')] # Choices list assigned after form instantiation to create a dynamic drop-down list. Consists of all department names stored in Departments table records.
    if form.validate_on_submit(): # Executes following sequence if it is a POST request (i.e. form submission) and it is validated.
        staff = Staff(staff_name=form.staff_name.data, email=form.email.data, department_id=form.department.data) # Instantiates new object of Staff class with staff_name, email and department_id passed in the form submission object.
        staff.last_sent = (datetime.datetime.utcnow() - datetime.timedelta(days=30)) # Initialises last_sent as 30 days prior to adding the staff member to the database.
        db.session.add(staff) # Adds new staff member record to the Staff table of the database.
        db.session.commit() # Commits database changes.
        flash('New staff added!') # Feedbacks to the system administrator that the new staff member record has successfully been added to the database.
        return redirect(url_for('main.index')) # Returns a redirect to the current /index page as a GET request.
    page = request.args.get('page', 1, type=int) # Implements page number as a query string argument called 'page' in the page's URL, default page is 1 and the page number data type is integer.
    staff = Staff.query.order_by(Staff.staff_name).paginate(page, current_app.config['POSTS_PER_PAGE'], True) # Returns pagination object which contains POSTS_PER_PAGE (assigned in 'config.py') number of desired records of the Staff table, ordered by descending staff_name
                                                                                                               # alphabetically for the corresponding page number. The False argument returns an empty page instead of HTTP status code 404 (Not Found) for a non-existing page.
    if staff.has_next: # staff.has_next returns True if there is at least one more page after the current page
        next_url = url_for('main.index', page=staff.next_num) # Sets next_url to URL for the next page, with the page number for the next page retrieved from staff.next_num
    else:
        next_url = None
    if staff.has_prev: # staff.has_prev returns True if there is at least one more page before the current page
        prev_url = url_for('main.index', page=staff.prev_num) # Sets prev_url to URL for the previous page, with the page number for the previous page retrieved from staff.prev_num
    else:
        prev_url = None
    return render_template('index.html', title='Dashboard', form=form, staff=staff.items, next_url=next_url, prev_url=prev_url)
    # Renders the template 'index.html' located in the 'main' directory of templates, with page title 'Dashboard', and passing the form object, staff.items (list of items in the requested page),
    # URL for the next page of results, and the URL for the previous page of results.

@bp.route('/staff/<staffid>', methods=['GET', 'POST']) # This page displays the details of the staff member record with id <staffid>, providing functionality to manually send a test phishing email to the staff member, or remove their record from the database.
@login_required
def staff(staffid): # staffid parameter is the value passed in the /<staffid> dynamic component of the URL
    sendEmailForm = SendEmail() # Instantiates an object of the SendEmail class. This form is used to manually send a test phishing email to the staff member.
    scheduleEmailForm = ScheduleEmail() # Instantiates an object of the ScheduledEmail class. This form is used to manually schedule a test phishing email for the staff member.
    removeStaffForm = RemoveStaffForm() # Instantiates an object of the RemoveStaffForm class. This form is used to remove the staff member's record from the database.
    staff = Staff.query.filter_by(id=staffid).first_or_404() # Queries the Staff table of the database, returning the first Staff record indexed with the primary key id passed as the argument to the view function.
                                                             # Otherwise, returns HTTP status code 404 (Not Found) if no record exists with id <staffid>
    if sendEmailForm.sendSubmit.data and sendEmailForm.validate_on_submit(): # Executes following sequence if sendEmailForm is submitted with a POST request and the data submitted is validated, and also that it is the sendEmailForm's sendSubmit field that was entered,
                                                                             # and not any other forms. This prevents multiple form submission clashes.
        template = sendEmailForm.selection.data # Assigns the template name selected by the user and passed as the data in the submitted form object to the variable 'template'.
        send_phishing_email(staff, template) # Invokes the send_email() function to create a background thread of the mail.send() method, sending the email to the staff member, with selected email template. The staff's record object is passed as the first parameter.
        flash('Phishing email sent, awaiting responses.')
        return redirect(url_for('main.staff', staffid=staff.id)) # Returns a redirect to the current /staff/<staffid> page as a GET request, passing the <staffid> as the query string argument.
    if scheduleEmailForm.scheduleSubmit.data and scheduleEmailForm.validate_on_submit():
        scheduled_email = ScheduledEmails(staff_email=staff.email, template=scheduleEmailForm.selection.data, send_time=scheduleEmailForm.datetime, staff=staff) # Instantiates new object of ScheduledEmails class with template, send_time and target email passed in the
                                                                                                                                                                 # form submission object and query string argument.
        db.session.add(scheduled_email) # Adds the new ScheduledEmails record to the database.
        db.session.commit()
        flash('Phishing email scheduled.')
        return redirect(url_for('main.staff', staffid=staff.id))
    if removeStaffForm.removeSubmit.data and removeStaffForm.validate_on_submit(): 
        department = Departments.query.get(staff.department_id) # Queries the Departments table of the database, returning the first Departments record indexed with the Staff record's foreign key, department_id.
        db.session.delete(staff) # Deletes the staff member's record from the database.
        recalculate_dep_risk(department) # Need to re-calculate department risk_score with this staff member now removed.
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('staff.html', title='Staff Profile', staff=staff, department=Departments.query.get(staff.department_id), send_form=sendEmailForm, schedule_form=scheduleEmailForm, remove_form=removeStaffForm)

@bp.route('/<page>/<staffid>', methods=['GET', 'POST']) # This page acts as the landing page staff members will redirect to if they click on the link provided in the test phishing emails. <page> is the template, i.e. Office, Dropbox, etc. and <staffid> acts as a
                                                        # unique identifier to which staff member clicked on the link, such that their risk score can be re-calculated.
def landingpage(page, staffid):
    form = LandingPage() # Instantiates an object of the LandingPage class. This form is used to detect if a staff member has submitted data to the test phishing site.
    if request.method == "GET": # Executes following sequence if the page has been accessed as a GET request, i.e. the test phishing email link has been clicked, which pushes a GET request to this page.
        staff = Staff.query.filter_by(id=staffid).first()
        department = Departments.query.get(staff.department_id)
        staff.clicked += 1 # Increments staff's clicked attribute by 1
        staff.latest_risk = 30 # Assigns staff member's latest_risk score to 30, which corresponds to a staff member clicking on the link but not submitting data.
        if staff.clicked == 1: # If it is the first time the staff member's risk score has been calculated (first time clicking a link), an average does not need to be found, the risk score is just set to 30.
            staff.risk_score += 30
            staff.direction = False # Staff member's risk direction is set to increasing as they have increased risk score from 0 to 30.
        else:
            new_risk = (staff.risk_score + 30)/2 # New average risk score is calculated by summing the staff member's existing average risk score with 30, and finding the average by dividing by 2.
            if (new_risk - staff.risk_score) > 0: # If the staff member's average risk score has increasing, they are set to increasing risk. Otherwise they will be set to decreasing risk.
                staff.direction = False
            elif (new_risk - staff.risk_score) < 0:
                staff.direction = True
            staff.risk_score = new_risk
        recalculate_dep_risk(department) # Staff member's department's average risk score is re-calculated now that their average risk score has updated.
        db.session.commit() # Commits database changes.
    if request.method == "POST": # Executes following sequence if the page has been accessed as a POST request, i.e. the landing page form has been submitted by the staff member. Do not need to check form validation.
        staff = Staff.query.filter_by(id=staffid).first()
        department = Departments.query.get(staff.department_id)
        staff.submitted += 1 # Increments staff's submitted attribute by 1
        staff.latest_risk = 100 # Assigns staff member's latest_risk score to 100, which corresponds to a staff member clicking on the link (+30) and then submitting data to the form (+70).
        if staff.clicked == 1: # If it is the first time the staff member has clicked on a phishing link, an average does not need to be found, their risk score is just incremented by 70.
                               # This means their total risk score will be 100 as they have to have clicked on the link (+30) prior to submitting.
            staff.risk_score += 70
        else:
            new_risk = ((staff.risk_score * 2) + 70)/2 # New average risk score is calculated by considering the actions of clicking on a link, and clicking and then submitting data as two independent events.
            if (new_risk - ((staff.risk_score * 2) - 30)) > 0:
                staff.direction = False
            elif (new_risk - ((staff.risk_score * 2) - 30)) < 0:
                staff.direction = True
            staff.risk_score = new_risk
        # Need to look at it as click or (click + submit)... because if you're submitting, you have to have clicked on the link first.
        # Therefore, we do the average for clicking, however if they then submit, we reset the calculation and calculate average for (click + submit)
        # Reverse calculation: *2, -30... then + 100, /2
        # This can be simplified as: *2, +70, /2
        recalculate_dep_risk(department)
        db.session.commit()
        return redirect(("http://www.{}.com/").format(page)) # Returns a redirect to the real template's website, i.e. https://www.office.com. This provides a sense of legitimacy for the staff member to avoid suspicion.
    return render_template(('landingpages/{}.html').format(page), title='Landing Page', staff=staff, form=form) # Renders the template '{}.html' where {} is formatted with the template name, i.e. 'office.html', located in the 'landingpages' directory of templates,
                                                                                                                # with page title 'Landing Page', and passing the staff and form objects for rendering.

@bp.route('/staff/<staffid>/edit', methods=['GET', 'POST']) # This page is used by the system administrator edit a specific staff member's profile details.
@login_required
def edit_staff(staffid):
    editStaffForm = EditStaffForm() # Instantiates an object of the EditStaffForm class. This form is used by the system administrator to edit the fields of the Staff record with id <staffid>, passed as the query string argument in the page URL.
    resetRiskForm = ResetRiskScoreForm() # Instantiates an object of the ResetRiskScoreForm class. This form is used by the system administrator to reset the risk score details of the Staff record with id <staffid> upon submission of the form.
    editStaffForm.department.choices = [(i.id, i.department_name) for i in Departments.query.order_by('department_name')] # Choices list assigned after editStaffForm instantiation to create a dynamic drop-down list. 
                                                                                                                          # Consists of all department names stored in Departments table records.
    if editStaffForm.editSubmit.data and editStaffForm.validate_on_submit():
        staff = Staff.query.filter_by(id=staffid).first()
        department = Departments.query.get(staff.department_id)
        staff.staff_name = editStaffForm.staff_name.data # Sets Staff record's fields to data submitted in editStaffForm object.
        before_edit_risk = staff.risk_score
        staff.email = editStaffForm.email.data
        staff.department_id = editStaffForm.department.data
        staff.risk_score = editStaffForm.risk_score.data
        recalculate_dep_risk(department) # Need to re-calculate department risk score with this staff member's new risk score. Or, if they have been moved departments - this counts as the department being moved from.
        new_department = Departments.query.get(editStaffForm.department.data)
        recalculate_dep_risk(new_department) # Need to re-calculate department risk score of department the staff member is being moved to, if they are being moved.
        after_edit_risk = staff.risk_score
        if after_edit_risk > before_edit_risk: # Changes the staff member's risk score direction (increasing/decreasing) depending on how their risk score is manually changed.
            staff.direction = False
        elif after_edit_risk < before_edit_risk:
            staff.direction = True
        db.session.commit()
        flash('Staff details have been updated.')
        return redirect(url_for('main.edit_staff', staffid=staff.id)) # Returns a redirect to the current /staff/<staffid>/edit page as a GET request, passing the <staffid> as the query string argument. This follows the Post/Redirect/Get pattern.
    if resetRiskForm.resetSubmit.data and resetRiskForm.validate_on_submit():
        staff = Staff.query.filter_by(id=staffid).first()
        department = Departments.query.get(staff.department_id)
        staff.risk_score = 0 # Resets Staff record's risk score fields upon validated POST request (i.e. form submission). This assigns them to their respective default values as defined in the 'models.py' module.
        staff.delivered = 0
        staff.clicked = 0
        staff.submitted = 0
        staff.latest_risk = 0
        staff.direction = False
        flash('Staff risk score details have been reset.')
        recalculate_dep_risk(department) # Need to re-calculate department risk_score with this staff member's new reset risk score.
        db.session.commit()
        ### This is required to prevent the form contents from being cleared upon resetRiskForm submission.
        editStaffForm.staff_name.data = staff.staff_name
        editStaffForm.email.data = staff.email
        editStaffForm.department.data = staff.department_id
        editStaffForm.risk_score.data = round(staff.risk_score, 1)
        ###
    elif request.method == 'GET': # This will show the default for a GET request as the form filled with existing staff details. Therefore, any fields that are not altered in the form will be set to their existing values upon form submission.
        staff = Staff.query.filter_by(id=staffid).first()
        editStaffForm.staff_name.data = staff.staff_name
        editStaffForm.email.data = staff.email
        editStaffForm.department.data = staff.department_id
        editStaffForm.risk_score.data = round(staff.risk_score, 1) # The round() function returns a floating point number that is the rounded version of staff.risk_score to 1 decimal place.
    staff = Staff.query.filter_by(id=staffid).first_or_404() # If the page is accessed with a GET request, returns Staff record with id <staffid>. Otherwise returns HTTP status code 404 (Not Found) if no record exists with id <staffid>
    return render_template('edit_staff.html', title='Edit Staff Profile', staff=staff, department=Departments.query.get(staff.department_id), edit_form=editStaffForm, reset_form=resetRiskForm)
