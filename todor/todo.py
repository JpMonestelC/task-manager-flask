import logging

from flask import Blueprint, render_template, request, redirect, url_for, g, flash, abort
from todor.auth import login_required
from .models import Todo
from todor import db

bp = Blueprint('todo', __name__, url_prefix='/todo')
logger = logging.getLogger(__name__)


@bp.route('/list')
@login_required
def index():
    """Show the current user's tasks, grouped by state in the template."""
    # Filter in the SQL query, don't pull the whole table and filter in the
    # template - with many users that older approach scaled very badly.
    todos = Todo.query.filter_by(created_by=g.user.id).all()
    return render_template('todo/index.html', todos=todos)


@bp.route('/create', methods=('POST',))
@login_required
def create():
    """Create a new task owned by the current user."""
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
    """Fetch a task by id, enforcing that it belongs to the current user."""
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
    """Update a task's title, description and/or state."""
    # Resolve the task (and enforce ownership) *outside* the try block, so a
    # 404 from get_todo() propagates as a real 404 instead of being caught by
    # the broad "except Exception" below and turned into a redirect.
    todo = get_todo(id)
    try:
        if request.method == 'POST':
            todo.title = request.form['title']
            todo.desc = request.form['desc']

            # Only accept one of the model's known state values - anything
            # else (missing field, stale/garbled client) leaves the state
            # untouched instead of silently storing junk.
            state_value = request.form.get('state')
            if state_value in Todo.STATES:
                todo.state = state_value

            db.session.commit()
        return redirect(url_for('todo.index'))
    except Exception:
        logger.exception("Failed to update todo %s", id)
        flash("Internal error, try again")
        return redirect(url_for('todo.index'))


@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Delete a task owned by the current user."""
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
