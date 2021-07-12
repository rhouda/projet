from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, logout_user, login_required, current_user, LoginManager
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import func
from datetime import datetime
import json
# from flask_security import bcrypt

app = Flask(__name__)

app.secret_key = "Secret key"

# SqlAlchemy Database Configuration With Mysql
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:'root@sql'@localhost/ewadb"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ewa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Data.query.get(int(user_id))

# Creating model table for our CRUD database
class Data(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(100))
    status = db.Column(db.String(100))
    company = db.Column(db.String(100))
    activity = db.Column(db.String(100))
    diplome = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    date_create = db.Column(db.DateTime, default=datetime.utcnow)
    city = db.Column(db.String(100))
    password = db.Column(db.String(128))

    def __init__(self, firstname, lastname, email, status, company, activity, diplome, phone, date_create, city, password):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.status = status
        self.company = company
        self.activity = activity
        self.diplome = diplome
        self.phone = phone
        self.date_create = date_create
        self.city = city
        self.password = password


@ app.route('/')
def Index():
    return render_template("login.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@ app.route('/profile')
@login_required
def profile():
    if current_user.is_authenticated:
        return render_template("profile.html")

    return redirect(url_for("login.html"))


@ app.route('/login')
def login():
    return render_template("login.html")


@ app.route('/etudiants')
# @login_required
def etudiants():
    allStudents = Data.query.filter(Data.email != "admin@gmail.com").all()
    return render_template("etudiants.html", students=allStudents)


@ app.route('/dashboard')
@login_required
def dashboard():
    students_by_city = db.session.query(Data.city, db.func.count(
        Data.city)).group_by(db.func.LOWER(Data.city)).filter(Data.email != "admin@gmail.com").limit(10).all()

    students_by_diplome = db.session.query(Data.diplome, db.func.count(
        Data.diplome)).group_by(db.func.LOWER(Data.diplome)).filter(Data.email != "admin@gmail.com").limit(10).all()

    students_by_statut = db.session.query(Data.status, db.func.count(
        Data.status)).group_by(db.func.LOWER(Data.status)).filter(Data.email != "admin@gmail.com").limit(10).all()

    total_students_c = []
    cities = []

    for city, nbrStud in students_by_city:
        cities.append(city)
        total_students_c.append(nbrStud)

    total_students_d = []
    diplomes = []

    for diplome, nbrStud in students_by_diplome:
        diplomes.append(diplome)
        total_students_d.append(nbrStud)

    total_students_s = []
    status_pro = []

    for status, nbrStud in students_by_statut:
        status_pro.append(status)
        total_students_s.append(nbrStud)

    print(total_students_s,status_pro)

    return render_template("dashboard.html", dataCities=json.dumps(cities), dataStudentsC=json.dumps(total_students_c),
                           dataDiplomes=json.dumps(diplomes), dataStudentsD=json.dumps(total_students_d),
                              dataStatus=json.dumps(status_pro), dataStudentsS=json.dumps(total_students_s))


@ app.route("/signup", methods=['POST'])
def signup_post():
    firstname = request.form["firstname"]
    lastname = request.form["lastname"]
    email = request.form["email"]
    status = request.form["status"]
    company = request.form["company"]
    activity = request.form["activity"]
    diplome = request.form["diplome"]
    phone = request.form["phone"]
    city = request.form["city"]
    password = generate_password_hash(request.form["pw"], method='sha256')
    date = datetime.now()

    user = Data.query.filter_by(email=email).first()

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('login'))

    myData = Data(firstname, lastname, email, status, company,activity, diplome, phone, date, city, password)
    db.session.add(myData)
    db.session.commit()

    return redirect(url_for('login'))


@app.route("/login", methods=["POST"])
def signin_post():
    email = request.form.get("email")
    password = request.form.get("password")

    student = Data.query.filter_by(email=email).first()
    print(type(student))
    if not student or not check_password_hash(student.password, password):
        flash('Please check your login details and try again.')
        # if user doesn't exist or password is wrong, reload the page
        return render_template("login.html")

    login_user(student)
    return redirect(url_for("profile"))

@app.route("/updatePage")
@login_required
def update_profile():
    return render_template("updateProfile.html")

@app.route("/update", methods=["POST"])
def update_post():
    user = Data.query.get(current_user.id)

    user.firstname = request.form["firstname"]
    user.lastname = request.form["lastname"]

    user.status = request.form["status"]
    user.company = request.form["company"]
    user.activity = request.form["activity"]
    user.diplome = request.form["diplome"]
    user.phone = request.form["phone"]
    user.city = request.form["city"]

    user.date = datetime.now()
    # db.session.add(myData)
    db.session.commit()
    flash('Les modifications sont bien faites')

    return redirect(url_for('profile'))

@app.route("/delete/<id>", methods=["GET", "POST"])
def delete_student(id):
    student =  Data.query.get(id)
    db.session.delete(student)
    db.session.commit()
    flash("l'etudiant(e) est supprime")

    return redirect(url_for('etudiants'))



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
