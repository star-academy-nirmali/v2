from flask import Flask, render_template, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), 'instance', 'star_academy.db')
 # SQLite database
db = SQLAlchemy(app)

# Define base paths for results and syllabus PDFs
RESULTS_FOLDER = os.path.join(os.getcwd(), 'results')
SYLLABUS_FOLDER = os.path.join(os.getcwd(), 'syllabus')

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    marks = db.Column(db.Integer, nullable=False)
    class_name = db.Column(db.String(50), nullable=False)

# Home Route
@app.route('/')
def home():
    db.session.expire_all()  # Clear cached data
    students_12th = Student.query.filter_by(class_name="12th").all()
    students_10th = Student.query.filter_by(class_name="10th").all()
    return render_template('index.html', students_12th=students_12th, students_10th=students_10th)

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
