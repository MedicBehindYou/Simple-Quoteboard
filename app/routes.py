#routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import db, login_manager
from app.models import User, Quote, Vote
from app.forms import RegistrationForm
from functools import wraps


bp = Blueprint('main', __name__)  # Create a blueprint

@bp.route('/')
def home():
    quotes = Quote.query.all()
    user_count = User.query.count()
    return render_template('home.html', quotes=quotes, user_count=user_count)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if User.query.count() >= 12:
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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/admin')
@login_required
@admin_required
def admin_panel():
    users = User.query.all()
    quotes = Quote.query.all()
    return render_template('admin.html', users=users, quotes=quotes)

@bp.route('/admin/quotes/edit/<int:quote_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    if request.method == 'POST':
        quote.content = request.form['content']
        quote.attribution = request.form['attribution']
        db.session.commit()
        flash('Quote updated successfully!')
        return redirect(url_for('main.admin_panel'))
    return render_template('edit_quote.html', quote=quote)

@bp.route('/admin/quotes/delete/<int:quote_id>', methods=['POST'])
@login_required
@admin_required
def delete_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    db.session.delete(quote)
    db.session.commit()
    flash('Quote deleted successfully!')
    return redirect(url_for('main.admin_panel'))

@bp.route('/admin/users/make_admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def make_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f'User {user.username} is now an admin.')
    return redirect(url_for('main.admin_panel'))

@bp.route('/quote/<int:quote_id>/upvote', methods=['POST'])
@login_required
def upvote(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    
    # Check if user has already voted on this quote
    existing_vote = Vote.query.filter_by(user_id=current_user.id, quote_id=quote_id).first()
    
    if existing_vote:
        if existing_vote.vote_type == 'upvote':
            return jsonify({'status': 'already_upvoted'}), 400
        else:
            # Change downvote to upvote
            existing_vote.vote_type = 'upvote'
            quote.upvotes += 1
            quote.downvotes -= 1

    else:
        # Create a new upvote
        vote = Vote(user_id=current_user.id, quote_id=quote_id, vote_type='upvote')
        quote.upvotes += 1

    db.session.commit()
    
    return jsonify({'status': 'success', 'upvotes': quote.upvotes, 'downvotes': quote.downvotes})

@bp.route('/quote/<int:quote_id>/downvote', methods=['POST'])
@login_required
def downvote(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    existing_vote = Vote.query.filter_by(user_id=current_user.id, quote_id=quote_id).first()

    if existing_vote:
        if existing_vote.vote_type == 'downvote':
            return jsonify({'status': 'already_downvoted'}), 400
        else:
            existing_vote.vote_type = 'downvote'
            quote.downvotes += 1
            quote.upvotes -= 1
    else:
        vote = Vote(user_id=current_user.id, quote_id=quote_id, vote_type='downvote')
        quote.downvotes += 1
        db.session.add(vote)

    db.session.commit()

    return jsonify({'status': 'success', 'upvotes': quote.upvotes, 'downvotes': quote.downvotes})

@bp.route('/vote/<vote_type>/<int:quote_id>', methods=['POST'])
@login_required
def vote(vote_type, quote_id):
    quote = Quote.query.get_or_404(quote_id)
    existing_vote = Vote.query.filter_by(user_id=current_user.id, quote_id=quote_id).first()

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            # User already voted this way, prevent further voting
            return jsonify({'status': f'already_{vote_type}d'}), 400
        else:
            # Change vote type (e.g., upvote to downvote or vice versa)
            if existing_vote.vote_type == 'upvote' and vote_type == 'downvote':
                quote.upvotes -= 1
                quote.downvotes += 1
            elif existing_vote.vote_type == 'downvote' and vote_type == 'upvote':
                quote.downvotes -= 1
                quote.upvotes += 1
            existing_vote.vote_type = vote_type
    else:
        # New vote
        if vote_type == 'upvote':
            quote.upvotes += 1
        elif vote_type == 'downvote':
            quote.downvotes += 1

        vote = Vote(user_id=current_user.id, quote_id=quote_id, vote_type=vote_type)
        db.session.add(vote)

    db.session.commit()

    # Return the updated vote count
    new_vote_count = quote.upvotes - quote.downvotes
    return jsonify(success=True, new_vote_count=new_vote_count)
