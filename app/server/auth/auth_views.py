
# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
from flask_login import login_user, logout_user , current_user , \
     login_required

from app.server.models import *
from app.server.auth.forms import EmailForm, PasswordForm
from app.server.utils import *


# Define the blueprint: 'auth', set its url prefix: app.url/auth
auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')

    username = request.form['username']
    password = request.form['password']
    remember_me = False
    if 'remember_me' in request.form:
        remember_me = True
    registered_user = Users.query.filter_by(username=username).first()
    # if the username or password is invalid
    if (registered_user is not None) and (registered_user.check_password(password)):
        login_user(registered_user, remember=remember_me)
        flash('Logged in successfully', 'success')
        return redirect(request.args.get('next') or url_for('main.home'))
    else:
        flash('Username or Password is invalid', 'error')
    return redirect(url_for('auth.login'))



@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        teams = Team.query.all()
        return render_template('auth/register.html', teams=teams)
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    team_id = request.form['team_id']

    username_exists, email_exists = False, False
    try:
        username_exists = Users.query.filter_by(username=username).first()
        email_exists = Users.query.filter_by(email=email).first()
    except:
        pass

    if username_exists or email_exists:
        flash("Sorry, an account with this username or email already exists", "error")
    else:
        try:
            print("team id is %s" % team_id)
            team = Team.query.get(team_id)
            user = Users(username,
                        password,
                        email,
                        team=team)
            db.session.add(user)
            db.session.commit()
            flash('User successfully registered', "success")
            #html = render_template('email/basic.html',
            #                       username=username)
            #send_email("Welcome to the attendance app!", email, html)
        except Exception as e:
            print("failed to create user: %s" % e)
            flash("Oops, something went wrong in creating your account" , "error")

    return redirect(url_for('auth.login'))


@auth.route('/reset', methods=["GET", "POST"])
def reset():
    form = EmailForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first_or_404()

        subject = "Password reset requested"

        # Here we use the URLSafeTimedSerializer we created in `util` at the
        # beginning of the chapter
        token = ts.dumps(user.email, salt='recover-key')

        recover_url = url_for(
            'reset_with_token',
            token=token,
            _external=True)

        html = render_template(
            'email/recover.html',
            recover_url=recover_url)

        # send_email is defined in myapp/util.py
        send_email(subject, user.email, html)

        flash('Check your email for a password reset link', "success")
        return redirect(url_for('main.index'))
    return render_template('auth/reset.html', form=form)


@auth.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    try:
        email = ts.loads(token, salt="recover-key", max_age=86400)
    except:
        abort(404)

    form = PasswordForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(email=email).first_or_404()

        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()
        flash("Password reset successfully", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_with_token.html', form=form, token=token)
