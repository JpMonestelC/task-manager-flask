import logging

from flask import Blueprint, render_template, request, redirect, url_for, g, jsonify, flash, abort
from todor.auth import login_required
from .models import Todo, User
from todor import db

bp = Blueprint('todo', __name__, url_prefix='/todo')
logger = logging.getLogger(__name__)


@bp.route('/list')
@login_required
def index():
    # Filtrar en la consulta SQL, no traer la tabla completa y filtrar en la
    # plantilla - con muchos usuarios esa versión anterior escalaba muy mal.
    todos = Todo.query.filter_by(created_by=g.user.id).all()
    return render_template('todo/index.html', todos=todos)


@bp.route('/create', methods=('POST',))
@login_required
def create():
    try:
        title = request.form['title']
        desc = request.form['desc']

        todo = Todo(g.user.id, title, desc)

        db.session.add(todo)
        db.session.commit()

        return redirect(url_for('todo.index'))
    except Exception:
        logger.exception("Failed to create todo")
        flash("Internal error, try again")
        return redirect(url_for('todo.index'))


def get_todo(id):
    # get_or_404 alone would let any logged-in user fetch (and, worse, edit
    # or delete) another user's task just by guessing its id - only return
    # tasks owned by the current user.
    todo = Todo.query.get_or_404(id)
    if todo.created_by != g.user.id:
        abort(404)
    return todo


@bp.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    # Resolve the task (and enforce ownership) *outside* the try block, so a
    # 404 from get_todo() propagates as a real 404 instead of being caught by
    # the broad "except Exception" below and turned into a redirect.
    todo = get_todo(id)
    try:
        if request.method == 'POST':
            todo.title = request.form['title']
            todo.desc = request.form['desc']

            state_value = request.form.get('state')
            if state_value == 'none':
                todo.state = None
            elif state_value == 'false':
                todo.state = False
            elif state_value == 'true':
                todo.state = True

            db.session.commit()
        return redirect(url_for('todo.index'))
    except Exception:
        logger.exception("Failed to update todo %s", id)
        flash("Internal error, try again")
        return redirect(url_for('todo.index'))


@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    # Same reasoning as update(): resolve/authorize before the try block.
    todo = get_todo(id)
    try:
        db.session.delete(todo)
        db.session.commit()

        return redirect(url_for('todo.index'))
    except Exception:
        logger.exception("Failed to delete todo %s", id)
        flash("Internal error, try again")
        return redirect(url_for('todo.index'))

