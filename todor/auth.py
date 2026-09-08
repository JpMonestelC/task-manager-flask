import functools
import logging
import re

from flask import Blueprint, render_template, request, url_for, redirect, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from todor import db

bp = Blueprint('auth', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Create a new account, checking format and uniqueness of the input."""
    try:
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = request.form['password']
            email = request.form['email'].lower()

            # Basic format check - keeps an obviously malformed address out
            # of the database even if a request bypasses the client-side
            # check in register.html.
            if not EMAIL_RE.match(email):
                flash("Please enter a valid email address.")
                return render_template('auth/register.html')

            try:
                user = User(username, generate_password_hash(password), email)
            except ValueError as exc:
                # Raised by User.validate_username (models.py) - the model
                # is the single source of truth for the username format.
                flash(str(exc))
                return render_template('auth/register.html')

            error = None

            user_name = User.query.filter_by(username=username).first()
            user_email = User.query.filter_by(email=email).first()

            if user_name is None and user_email is None:
                db.session.add(user)
                db.session.commit()
                flash("User registered successfully!")  # Success message
                return redirect(url_for('auth.login'))
            else:
                if user_name:
                    error = f"Username '{username}' is already registered"
                elif user_email:
                    error = f"Email '{email}' is already registered"

            flash(error)  # Show the error if the username or email is taken


        return render_template('auth/register.html')
    except Exception:
        logger.exception("Failed to register user")
        flash("Internal error, try again")
        return render_template('auth/register.html')


@bp.route('/login', methods = ('GET', 'POST'))
def login():
    """Authenticate a user and start their session."""
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            error = None

            # Validate credentials
            user = User.query.filter_by(username=username).first()
            if user is None:
                error = "Incorrect username or password"
            elif not check_password_hash(user.password_hash, password):
                error = "Incorrect password"

            # Start the session
            if error is None:
                session.clear()
                session['user_id'] = user.id
                return redirect(url_for('todo.index'))

            flash(error)


        return render_template('auth/login.html')
    except Exception:
        logger.exception("Failed to log in user")
        flash("Internal error, try again")
        return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    """Populate g.user for every request from the session, if any."""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        # A plain get_or_404 here would 500/404 every request for a session
        # left over from a deleted account instead of just logging the
        # visitor out - fall back to an anonymous session in that case.
        g.user = User.query.get(user_id)
        if g.user is None:
            session.clear()

@bp.route('/logout')
def logout():
    """Clear the session and send the visitor back to the home page."""
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    """Redirect anonymous visitors to the login page before running view."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
