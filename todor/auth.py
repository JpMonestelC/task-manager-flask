import logging
import re
from flask import Blueprint, render_template, request, url_for, redirect, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from todor import db

bp = Blueprint('auth', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)

@bp.route('/register', methods=('GET', 'POST'))
def register():
    try:
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = request.form['password']
            email = request.form['email'].lower()

            # Validación del username
            if not re.match(r'^[a-zA-Z0-9_]+$', username):  # Solo letras, números y guiones bajos
                flash("El nombre de usuario solo puede contener letras, números y guiones bajos.")
                return render_template('auth/register.html')

            user = User(username, generate_password_hash(password), email)

            error = None

            user_name = User.query.filter_by(username=username).first()
            user_email = User.query.filter_by(email=email).first()

            if user_name is None and user_email is None:
                db.session.add(user)
                db.session.commit()
                flash("Usuario registrado exitosamente!")  # Mensaje de éxito
                return redirect(url_for('auth.login'))
            else:
                if user_name:
                    error = f"El usuario {username} ya está registrado"
                elif user_email:
                    error = f"El correo {email} ya está registrado"

            flash(error)  # Mostrar error si ya existe el usuario o el email


        return render_template('auth/register.html')
    except Exception:
        logger.exception("Failed to register user")
        flash("Internal error, try again")
        return render_template('auth/register.html')


@bp.route('/login', methods = ('GET', 'POST'))
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            error = None

            # Validar datos
            user = User.query.filter_by(username=username).first()
            if user is None:
                error = "Nombre de usuario o contraseña incorrectos"
            elif not check_password_hash(user.password, password):
                error = "Contraseña incorrecta"

            # Iniciar sesión
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
    session.clear()
    return redirect(url_for('index'))

import functools

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view