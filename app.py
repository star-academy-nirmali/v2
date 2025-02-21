from flask import Flask, render_template, send_from_directory, abort
from flask import request, redirect, url_for, flash
from flask import session
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
import bcrypt

# Store the hashed password (Replace this with a value from your database)
STORED_HASHED_PASSWORD = "$2b$12$TVy2MxySmDE0Lous2qTH.ejusaCWCJRNFSTd8nehSV0o45bDrmk36"  # Replace with actual hashed password

from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), 'instance', 'star_academy.db')
STUDENT_UPLOAD_FOLDER = os.path.join('static', 'images', 'Student')
BANNER_UPLOAD_FOLDER = os.path.join('static', 'images')

# Ensure directories exist
os.makedirs(STUDENT_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BANNER_UPLOAD_FOLDER, exist_ok=True)

 # SQLite database
db = SQLAlchemy(app)

# Define base paths for results and syllabus PDFs
RESULTS_FOLDER = os.path.join(os.getcwd(), 'results')
SYLLABUS_FOLDER = os.path.join(os.getcwd(), 'syllabus')


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200), nullable=False, default='default.png')  # Default image
    marks = db.Column(db.Integer, nullable=False)
    class_name = db.Column(db.String(50), nullable=False)


load_dotenv()  # Load environment variables from .env
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret')  # Needed for session management

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')  # Convert to bytes

        if username == 'admin' and bcrypt.checkpw(password, STORED_HASHED_PASSWORD.encode('utf-8')):
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials!', 'error')

    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.clear()  # Clears all session data
    return redirect(url_for('login.html'))


# Protect Admin Page
@app.before_request
def restrict_admin_access():
    if request.endpoint in ['admin_panel', 'update_student', 'delete_student'] and 'admin' not in session:
        return redirect(url_for('login'))

# Home Route
@app.route('/')
def home():
    db.session.expire_all()  # Clear cached data
    students_12th = Student.query.filter_by(class_name="12th").all()
    students_10th = Student.query.filter_by(class_name="10th").all()
    return render_template('index.html', students_12th=students_12th, students_10th=students_10th)

# Admin Panel Route - List all students
@app.route('/admin')
def admin():
    students = Student.query.all()
    return render_template('admin.html', students=students)
#update banner
@app.route('/update_banner', methods=['POST'])
def update_banner():
    if 'banner_image' not in request.files:
        flash("No file part", "error")
        return redirect(url_for('admin'))
    
    file = request.files['banner_image']
    if file.filename == '':
        flash("No selected file", "error")
        return redirect(url_for('admin'))

    filename = "star academy banner.jpg"  # Overwrite existing banner
    file_path = os.path.join(BANNER_UPLOAD_FOLDER, filename)
    file.save(file_path)

    flash("Banner updated successfully!", "success")
    return redirect(url_for('admin'))


# Update Student Route
@app.route('/update_student', methods=['POST'])
def update_student():
    student_id = request.form.get('id')
    student = db.session.get(Student, student_id)

    if not student:
        return "Student not found", 404

    student.name = request.form.get('name')
    student.marks = request.form.get('marks')
    student.class_name = request.form.get('class_name')

    # Handle image upload
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file_path = os.path.join(STUDENT_UPLOAD_FOLDER, filename)
            file.save(file_path)  # Save new image
            student.image = filename  

    db.session.commit()
    flash("Student updated successfully!", "success")
    return redirect(url_for('admin'))


@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        return "Student not found", 404

    db.session.delete(student)
    db.session.commit()
    return "Student deleted successfully"


# Route for results page
@app.route('/results/<int:class_name>')
def results(class_name):
    template_file = f"results {class_name}th.html"
    
    # Check if the template exists
    if os.path.exists(os.path.join('templates', template_file)):
        return render_template(template_file, class_name=class_name)
    else:
        return abort(404, description="Results page not found")

# Route for syllabus page
@app.route('/syllabus/<int:class_name>')
def syllabus(class_name):
    template_file = f"syllabus {class_name}th.html"

    # Check if the template exists
    if os.path.exists(os.path.join('templates', template_file)):
        return render_template(template_file, class_name=class_name)
    else:
        return abort(404, description="Syllabus page not found")

# Route for downloading results PDF
@app.route('/download/results/<int:class_name>')
def download_results_pdf(class_name):
    pdf_file = f'class {class_name}th result.pdf'

    if os.path.exists(os.path.join(RESULTS_FOLDER, pdf_file)):
        return send_from_directory(RESULTS_FOLDER, pdf_file, as_attachment=True)
    else:
        return abort(404, description="Results PDF not found")

# Route for downloading syllabus PDF
@app.route('/download/syllabus/<int:class_name>')
def download_syllabus_pdf(class_name):
    pdf_file = f'START ACADEMY SYLLABUS {class_name}th.pdf'

    if os.path.exists(os.path.join(SYLLABUS_FOLDER, pdf_file)):
        return send_from_directory(SYLLABUS_FOLDER, pdf_file, as_attachment=True)
    else:
        return abort(404, description="Syllabus PDF not found")

if __name__ == '__main__':
    app.run(debug=True)
