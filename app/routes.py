from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db, login_manager
from app.models import User, Quote
from app.forms import RegistrationForm

bp = Blueprint('main', __name__)  # Create a blueprint

@bp.route('/')
def home():
    quotes = Quote.query.all()
    user_count = User.query.count()
    return render_template('home.html', quotes=quotes, user_count=user_count)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if User.query.count() >= 10:
        flash('Registration limit reached. Cannot register more users.', 'warning')
        return redirect(url_for('main.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        print('Form is valid')
        try:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')
            print(f'Exception: {e}')
    else:
        print('Form is not valid')
        print(form.errors)

    return render_template('register.html', title='Register', form=form)



@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@bp.route('/submit_quote', methods=['POST'])
@login_required
def submit_quote():
    content = request.form['content']
    attribution = request.form['attribution']

    if len(content) > 512:
        flash('Quote cannot be more than 512 characters.')
        return redirect(url_for('main.home'))

    quote = Quote(content=content, attribution=attribution, user_id=current_user.id)
    db.session.add(quote)
    db.session.commit()
    return redirect(url_for('main.home'))

@bp.route('/profile')
@login_required
def profile():
    user = current_user
    return render_template('profile.html', user=user)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
