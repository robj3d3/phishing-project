from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user
from app.auth import bp
from app.auth.forms import AdminLoginForm, AdminRegistrationForm
from app.models import Admin
from app import db

from urllib.parse import urlparse, urljoin

def is_safe_url(target): # Returns boolean value, True if target redirect is relative, False if otherwise.
    ref_url = urlparse(request.host_url) # urlparse() parses URL into its six components, returning a 6-tuple.
    test_url = urlparse(urljoin(request.host_url, target)) # urljoin() constructs an absolute URL by combining the first argument URL (the base URL) with the target URL,
                                                           # providing missing components in the relative URL.
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc # netloc is the 'www.test.co.uk:80' component of the URL - short for network location
                                             # scheme is the 'http' or 'https' component of the URL

@bp.route('/login', methods=['GET', 'POST']) # Decorator registers the /login route with the login() view function, accepting only GET and POST requests to the page. This page is used for system administrator logins.
def login():
    if current_user.is_authenticated: # current_user is a proxy object, similar to application and request contexts, that points to the current user.
                                      # is_authenticated is an attribute inherited from the UserMixin class, and returns True if the user is authenticated (i.e. logged in with valid credentials).
        return redirect(url_for('main.index')) # Returns a response object that redirects the client to the target location provided passed as the argument using the url_for() function.
                                               # url_for() function returns the URL to the given endpoint, here being 'main.index', i.e. the index view function in the main directory.
    no_account = False # Need to pass Boolean to Jinja for rendering - when no admin account is registered (no_account=False), the registration page hyperlink will be rendered.
    if len(list(Admin.query.all())) == 0:
        no_account = True
    form = AdminLoginForm() # Instantiates an object of the AdminLoginForm class. This form is used to log in the sytem administrator to the application using login credentials.
    if form.validate_on_submit(): # form.validate_on_submit() will return True if it is a POST request (i.e. the form has been submitted) and the form contents have been validated.
        user = Admin.query.filter_by(username=form.username.data).first() # Queries the Admin table of the database, returning the first record/object which has the username attribute
                                                                          # equal to the username submitted in the form, or None if no such record exists.
        if user is None or not user.check_password(form.password.data): # If no record with the submitted credentials was found, or the password entered does not match, executes following sequence.
            flash('Invalid login credentials.') # Feedbacks to the user that they have entered invalid login credentials.
            return redirect(url_for('auth.login')) # Returns a redirect to the current login page as a GET request. This follows the Post/Redirect/Get pattern which aims to prevent duplicate form submissions.
        login_user(user, force=True) # Otherwise, assuming login credentials are correct, logs in the user corresponding to the object previously queried. force=True ensures user is logged in even if account is deemed inactive.
        next_page = request.args.get('next') # Returns the value of the 'get' variable in the URL, if one is provided. If a user has previously attempted to access another view function in the application without
                                             # being logged in, this value will be set to that route endpoint. Therefore, subsequent to logging in the user is redirected to the page they were attempting to access prior.
        if not is_safe_url(next_page):
            return flask.abort(400) # If the redirect would have been external, aborts the request with HTTP error code 400 (Bad Request)
        return redirect(next_page or url_for('main.index')) # Returns a redirect to the next_page value if it is an internal redirect, otherwise redirects to the /index page.
    return render_template('auth/login.html', title='Admin Sign In', form=form, no_account=no_account) # Renders the template 'login.html' located in the 'auth' directory of templates, with page title 'Admin Sign In', and passing the form
                                                                                                       # object and no_account boolean value for rendering in the template.

@bp.route('/register', methods=['GET', 'POST']) # This page is used for system administrator account registration. A maximum of 1 system administrator account is allowed to be registered.
def register():
    if current_user.is_authenticated or len(list(Admin.query.all())) > 0: # Executes following sequence if the current user is already authenticated (logged in) or a system administrator account has already been registered (a max of 1 is allowed).
        flash('Administrator account already exists.')
        return redirect(url_for('main.index'))
    form = AdminRegistrationForm() # Instantiates an object of the AdminRegistrationForm class. This form is used to register a new system administrator account record, provided a username and password.
    if form.validate_on_submit(): # Executes following sequence if it is a POST request and it is validated.
        admin = Admin(username=form.username.data) # Instantiates object of Admin class, creating a system administrator user record in the Admin table, with 
        admin.set_password(form.password.data) # Sets the user's password using the SHA256 hash function. The user's password is not stored anywhere as a hardcoded string.
        db.session.add(admin) # Adds the new Admin record to the database.
        db.session.commit() # Commits database changes to the database.
        flash('Admin account registered.') # Feedbacks to the user that they have successfully registered a system administrator account.
        return redirect(url_for('auth.login')) # Returns a redirect to the login page for the user to sign in with their registered credentials.
    return render_template('auth/register.html', title='Register Admin Account', form=form)