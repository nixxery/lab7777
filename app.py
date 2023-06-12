from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, abort
from flask_restx import Api, Resource, fields
from database import db, Books, initialize_database



app = Flask(__name__)
app.secret_key = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Инициализация объекта Api
api = Api(app, version='1.0', title='Books API', description='API for managing book data')

# Определение модели студента
book_model = api.model('Book', {
    'book_name': fields.String(required=True, description='Full name of the student'),
    'author_name': fields.String(required=True, description='Subject of study'),
    'write_date': fields.Integer(required=True, description='Semester number'),
    'janre': fields.String(required=True, description='Semester number'),
})

# Пример данных о студентах
books = []

# Конечная точка для получения всех студентов
@api.route('/books')
class BooksResource(Resource):
    @api.doc('get_all_students')
    @api.marshal_list_with(book_model)
    def get(self):
        return books

    @api.doc('create_book')
    @api.expect(book_model)
    @api.marshal_with(book_model, code=201)
    def post(self):
        payload = request.json
        book_name = payload['book_name']
        author_name = payload['author_name']
        write_date = payload['write_date']
        janre = payload['janre']
        new_book = {
            'book_name': book_name,
            'author_name': author_name,
            'write_date': write_date,
            'janre': janre,
        }
        books.append(new_book)
        return payload, 201

@api.route('/books/<string:book_name>')
@api.doc(params={'book_name': 'Full name of the book'})
class BookResource(Resource):
    @api.doc('get_book')
    @api.marshal_with(book_model)
    def get(self, book_name):
        for book in books:
            if book['book_name'] == book_name:
                return book
        api.abort(404, f'Student {book_name} not found')

    @api.doc('update_book')
    @api.expect(book_model)
    @api.marshal_with(book_model)
    def put(self, book_name):
        for book in books:
            if book['book_name'] == book_name:
                payload = request.json
                book['book_name'] = payload['book_name']  # Обновление имени студента
                book['author_name'] = payload['author_name']
                book['write_year'] = payload['write_year']
                book['janre'] = payload['janre']
                return book
        api.abort(404, f'Book {book_name} not found')

    @api.doc('patch_book')
    @api.expect(api.model('UpdateStudent', {
        'field': fields.String(required=True, description='Field to update'),
        'value': fields.String(required=True, description='New value')
    }))
    @api.marshal_with(book_model)
    def patch(self, book_name):
        payload = request.json
        field = payload['field']
        value = payload['value']
        if field not in Book.__table__.columns:
            abort(400, f'Field {field} does not exist')
        for book in books:
            if book['book_name'] == book_name:
                book[field] = value
                return book

        abort(404, f'Student with name {book_name} not found')
        setattr(book, field, value)
        db.session.commit()
        return book

    @api.doc('delete_book')
    @api.response(204, 'Student deleted')
    def delete(self, book_name):
        for book in books:
            if book['book_name'] == book_name:
                books.remove(book)
                return '', 204
        abort(404, f'Book {book_name} not found')

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(120), nullable=False)
    author_name = db.Column(db.String(120), nullable=False)
    write_date = db.Column(db.Integer, nullable=False)
    janre = db.Column(db.String(120), nullable=False)

    @staticmethod
    def get_all_sorted(attribute):
        if attribute == 'book_name':
            return Book.query.order_by(Book.book_name).all()
        elif attribute == 'author_name':
            return Book.query.order_by(Book.author_name).all()
        elif attribute == 'write_date':
            return Book.query.order_by(Book.grade.write_date()).all()
        elif attribute == 'janre':
            return Book.query.order_by(Book.janre).all()
        else:
            return Book.query.all()

    def __repr__(self):
        return f'<Book {self.book_name}>'


@app.route('/books', methods=['GET'])
def get_all_books():
    book = Books.query.all()
    return render_template('all_students.html', books=book)


@app.route('/add_student', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        book_name = request.form['book_name']
        author_name = request.form['author_name']
        write_name = request.form['write_name']
        janre = request.form['janre']
        new_book = Book(book_name=book_name, author_name=author_name, write_name=write_name, janre=janre)
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully')
        return redirect(url_for('get_all_students'))
    return render_template('add_student.html')


@app.route('/students/stats')
def get_book_stats():
    grades = [s.grade for s in Book.query.all()]
    average_grade = sum(grades) / len(grades)
    max_grade = max(grades)
    min_grade = min(grades)
    oldest_student = Book.query.order_by(Book.age.desc()).first()
    youngest_student = Book.query.order_by(Book.age.asc()).first()
    return render_template('stats.html', average_grade=average_grade, max_grade=max_grade, min_grade=min_grade,
                           oldest_student=oldest_student, youngest_student=youngest_student)


@app.route('/sort', methods=['GET', 'POST'])
def sort_students():
    if request.method == 'POST':
        attribute = request.form.get('attribute')
        students = Book.get_all_sorted(attribute)
        return render_template('all_students.html', students=students)
    else:
        students = Book.query.all()
        return render_template('sort_students.html', students=students)


@app.route('/update_student', methods=['GET', 'POST'])
def update_student():
    if request.method == 'POST':
        old_full_name = request.form['old_full_name']
        new_full_name = request.form['new_full_name']
        student = Book.query.filter_by(full_name=old_full_name).first()
        if not student:
            flash(f'Student {old_full_name} not found')
            return redirect(url_for('update_student'))
        student.full_name = new_full_name
        student.age = request.form['age']
        student.grade = request.form['grade']
        student.subject = request.form['subject']
        student.semester_number = request.form['semester_number']
        student.start_year = request.form['start_year']
        db.session.commit()
        flash(f'Student {old_full_name} updated successfully')
        return redirect(url_for('get_all_students'))
    else:
        return render_template('update_student.html')



# @app.route('/delete_student', methods=['GET', 'POST'])
# def delete_student():
#     if request.method == 'POST':
#         book_name = request.form['book_name']
#         student = Book.query.filter_by(book_name=book_name).first()
#         if not book:
#             flash(f'Student {book_name} not found')
#             return redirect(url_for('delete_book'))
#         db.session.delete(book)
#         db.session.commit()
#         flash(f'Student {book_name} deleted successfully')
#         return redirect(url_for('get_all_students'))
#     else:
#         return render_template('delete_student.html')
#
#


@app.route('/api')
def api():
    return redirect(url_for('swagger_ui', path='swagger.json'))


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    initialize_database(app)
    app.run(debug=True)
