from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(120), nullable=False)
    author_name = db.Column(db.String(120), nullable=False)
    write_date = db.Column(db.String, nullable=False)
    janre = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Books {self.book_name}>'

def initialize_database(app):
#    db.init_app(app)
    with app.app_context():
        db.create_all()
