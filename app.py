from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, RadioField, TextAreaField , DateField
from wtforms.validators import InputRequired, DataRequired, Email, Length, EqualTo
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from datetime import datetime
app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), 'users.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SECRET_KEY'] = 'helloworld'
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

class Card(db.Model):
    cardid = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, unique=False)
    title = db.Column(db.String(40), unique=False)
  #  taskid = db.Column(db.Integer, unique=False)

class Task(db.Model):
    taskid = db.Column(db.Integer, primary_key=True)
    cardid = db.Column(db.Integer, unique=False)
    id = db.Column(db.Integer, unique=False)
    title = db.Column(db.String(40), unique=False)
    description = db.Column(db.String(200), unique=False)
    #status = db.Column(db.String(10), unique=False)
    date = db.Column(db.DateTime, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')

class RegisterForm(FlaskForm):
    email = StringField('Email Address', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    confirm = PasswordField('Repeat Password', validators=[InputRequired(), EqualTo('password', message='Passwords must match')])

class CardForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(),Length(min=2, max=50)])

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(),Length(min=2, max=50)])
    description = TextAreaField('Description', validators=[InputRequired(), Length(min=4, max=200)])
    #status = RadioField('Status', choices=[for i in cardid ], validators=[InputRequired()])
    date = DateField('Date',validators=[DataRequired("Please enter the task's End Date.")] , default=datetime.now())



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return render_template('loginfail.html')

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return render_template('signupsuccess.html', form=form)

    return render_template('signup.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():

    cards = Card.query.filter_by(id=current_user.id).all()
    task = Task.query.filter_by(id=current_user.id).all()
 #   done = Task.query.filter_by(status='done',id=current_user.id).all()

    return render_template('dashboard.html', name = current_user.username, card = cards , task=task)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profile.html', name = current_user.username, email = current_user.email)

@app.route('/addcard', methods=['GET', 'POST'])
@login_required
def addcard():
    form = CardForm(request.form)

    if form.validate_on_submit():
        title = form.title.data

        new_card = Card(id=current_user.id, title=title)
        db.session.add(new_card)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('addcard.html', form=form)

@app.route('/addtask', methods=['GET', 'POST'])
@login_required
def addtask():
    form = TaskForm(request.form)

    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        date = form.date.data


        new_task = Task(id=current_user.id, title=title, description=description, date=date )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('addtask.html', form=form )

@app.route('/deletec/<cardid>', methods=['GET','POST'])
def deletec(cardid):
    deleted = Card.query.filter_by(cardid=int(cardid)).first()

    db.session.delete(deleted)
    db.session.commit()

    return redirect(url_for('dashboard'))

@app.route('/delete/<taskid>', methods=['GET','POST'])
def delete(taskid):
    deleted = Task.query.filter_by(taskid=int(taskid)).first()

    db.session.delete(deleted)
    db.session.commit()

    return redirect(url_for('dashboard'))
@app.route('/summary', methods=['GET','POST'])
@login_required
def summary():

    count_todo =Task.query.filter_by(id=current_user.id).all()


    return render_template('summary.html',todo= len(count_todo) )
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)