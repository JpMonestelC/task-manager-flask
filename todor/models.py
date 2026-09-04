from todor import db

# Modelo Usuarios
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)  
    email = db.Column(db.String(120), unique=True, nullable=False)  

    # Constructor
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        return f'<User: {self.username} >'

# Modelo Todo-list
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  
    title = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.Text)  
    state = db.Column(db.Boolean, default=None)

    # Constructor
    def __init__(self, created_by, title, desc, state=None):
        self.created_by = created_by
        self.title = title
        self.desc = desc
        self.state = state

    def __repr__(self):
        return f'<Todo: {self.title} >'
