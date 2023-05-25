from flask import Flask, render_template, url_for, redirect, request ,jsonify
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import awsgi
import boto3
import os
from uuid import uuid4


BASE_ROUTE = "/items"
TABLE = os.environ.get("STORAGE_SEOAUTODB_NAME")
client = boto3.client('dynamodb')


app = Flask(__name__)

CORS(app)

bcrypt = Bcrypt(app)



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))


class users(client.Model, UserMixin):
    id = client.Column(client.Integer, primary_key=True)
    username = client.Column(client.String(20), nullable=False, unique=True)
    password = client.Column(client.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = users.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "password"})

    submit = SubmitField('Login')


@app.route('/')
def index():
    return render_template('index.html')


# Route to handle login form submission
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = users.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.route('/service', methods=['GET', 'POST'])
def service():
    return render_template('service.html')


@app.route('/register', methods=['post'])
def register():
    if request.method == 'POST':

        client.put_item(TableName=TABLE, Item={'id': {'S': str(uuid4())},
                                               'username': {'S': request.form['username']},
                                               'password': {'S': request.form['password']}
                                               })

        msg = "Registration Complete. Please Login to your account !"

        return jsonify(message='login.html', msg=msg)
    return jsonify(message='success')


def handler(event, context):
    return awsgi.response(app, event, context)

if __name__ == "__main__":
    app.run(debug=True)

