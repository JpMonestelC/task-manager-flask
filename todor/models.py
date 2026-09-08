import re

from sqlalchemy.orm import validates

from todor import db

USERNAME_RE = re.compile(r'^[a-zA-Z0-9_]+$')


class User(db.Model):
    """A registered account. Owns zero or more Todo items."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, username, password_hash, email):
        self.username = username
        self.password_hash = password_hash
        self.email = email

    @validates('username')
    def validate_username(self, key, value):
        """Enforce the username format at the model level.

        This is the single source of truth for the rule: auth.py relies on
        this validator raising ValueError instead of duplicating the regex,
        and the matching check in register.html is only a client-side UX
        mirror (see the comment there).
        """
        if not USERNAME_RE.match(value):
            raise ValueError(
                "Username can only contain letters, numbers and underscores."
            )
        return value

    def __repr__(self):
        return f'<User: {self.username}>'


class Todo(db.Model):
    """A single task owned by a User, tracked through three states."""

    STATE_NOT_STARTED = 'not_started'
    STATE_IN_PROGRESS = 'in_progress'
    STATE_COMPLETED = 'completed'
    STATES = (STATE_NOT_STARTED, STATE_IN_PROGRESS, STATE_COMPLETED)

    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.Text)
    state = db.Column(db.String(20), nullable=False, default=STATE_NOT_STARTED)

    def __init__(self, created_by, title, desc, state=STATE_NOT_STARTED):
        self.created_by = created_by
        self.title = title
        self.desc = desc
        self.state = state

    def __repr__(self):
        return f'<Todo: {self.title}>'
