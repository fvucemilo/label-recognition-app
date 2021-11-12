import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

import model

load_dotenv()

app = Flask(__name__, template_folder='Template')
Bootstrap(app)

ENV = os.environ.get('ENV')

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:toor@localhost/label_recognition_db'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Wine(db.Model):
    __tablename__ = 'wines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    production_year = db.Column(db.String(200))
    manufacturer = db.Column(db.String(200))
    class_name = db.Column(db.String(200), unique=True)

    def __init__(self, name, production_year, manufacturer, class_name):
        self.name = name
        self.production_year = production_year
        self.manufacturer = manufacturer
        self.class_name = class_name

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            image_path = os.path.join('static/upload', uploaded_file.filename)
            uploaded_file.save(image_path)
            prediction = model.get_prediction(image_path)
            if db.session.query(Wine).filter(Wine.class_name == prediction['class_name']).count() != 0:
                data = db.session.query(Wine).filter(Wine.class_name == prediction['class_name']).one()
            else:
                data = None
            result = {
                'class_name': prediction['class_name'],
                'score': prediction['score'],
                'image_path': image_path,
                'data': data
            }
            return render_template('wine/result.html', result = result)
    data = db.session.query(Wine).all()
    result = {
        'data': data
    }
    return render_template('wine/index.html', result = result)

@app.route('/wine', methods=['GET','POST'])
def create_wine():
    if request.method == 'POST':
        name = request.form['name']
        production_year = request.form['production_year']
        manufacturer = request.form['manufacturer']
        class_name = request.form['class_name']
        if db.session.query(Wine).filter(Wine.class_name == class_name).count() == 0:
            new_data = Wine(name, production_year, manufacturer, class_name)
            db.session.add(new_data)
            db.session.commit()
    data = db.session.query(Wine).all()
    result = {
        'data': data
    }
    return render_template('wine/create.html', result = result)

@app.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        image = request.form['image']
        if image != '':
            image = os.path.join('static', image)
            os.remove(image)
    image_path = os.listdir('static/upload')
    image_path = ['upload/' + file for file in image_path]
    result = {
        'image_path': image_path
    }
    return render_template('upload/index.html', result = result)

if __name__ == '__main__':
    app.run()
