from flask import Blueprint, render_template, flash, url_for, redirect
from blog.forms import LoginForm
from flask_login import login_user, current_user, logout_user, login_required
from blog.models import Admin

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.first()
        if admin:
            if username == admin.username and admin.validate_password(password):
                login_user(admin, remember)
                flash('Welcome back.', 'info')
                return form.redirect()
            flash('Invalid username or password.', 'warning')
        else:
            flash('No account.', 'warning')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
	logout_user()
	flash('Logout success', 'info')
	return redirect('blog.index')