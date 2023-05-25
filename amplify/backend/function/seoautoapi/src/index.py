import awsgi
import boto3
import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from uuid import uuid4

#installation for storing the username
from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from json import JSONEncoder
import secrets


BASE_ROUTE = "/items"
TABLE = os.environ.get("STORAGE_SEOAUTODB_NAME")
client = boto3.client('dynamodb')


app = Flask(__name__)

# Handle CORS for the app
CORS(app)


@app.route(BASE_ROUTE, methods=['POST'])
def create_item():
    request_json = request.get_json()
    client.put_item(TableName=TABLE, Item={'id': {'S':str(uuid4())},
                                           'username': {'S': request_json.get('username')},
                                           'password': {'S': request_json.get('password')},
                                           'user_id': {'S': request_json.get('user_id')}
    })
    return jsonify(message="item created")


@app.route(BASE_ROUTE + '/<user_id>', methods=['GET'])
def get_user(user_id):
    user = client.get_item(TableName=TABLE, Key={
        'id': {
            'S': user_id
        }
    })
    return jsonify(data=user)


@app.route(BASE_ROUTE + '/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    client.delete_item(
        TableName=TABLE,
        Key={'id': {'S': user_id}}
    )
    return jsonify(message="user deleted")


@app.route(BASE_ROUTE + '/<user_id>', methods=['PUT'])
def update_user(user_id):
    # Change to your fields
    client.update_item(
        TableName=TABLE,
        Key={'id': {'S': user_id}},
        UpdateExpression='SET #username = :username, #password = :password, #user_id = :user_id',
        ExpressionAttributeNames={
            '#username': 'name',
            '#password': 'password',
            '#user_id': 'user_id'
        },
        ExpressionAttributeValues={
            ':username': {'S': request.json['username']},
            ':password': {'S': request.json['password']},
            ':user_id': {'S': request.json['user_id']},
        }
    )
    return jsonify(message="item updated")




@app.route(BASE_ROUTE, methods=['GET']) 
def list_items():
    return jsonify(data=client.scan(TableName=TABLE) )

  
def handler(event, context):
    return awsgi.response(app, event, context)


# app = Flask(__name__)
# db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:seoautodb@database-2.citfvzt9dntl.eu-north-1.rds.amazonaws.com/kTestDb'
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)


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



@ app.route('/register', methods=['GET', 'POST'])
def register():

    form = RegisterForm()


    if form.validate_on_submit():
        # Handle form submission and save data to DynamoDB
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = users(username=form.username.data, password=hashed_password)
        client.session.add(new_user)

        client.session.commit()
        return redirect('login')

    return render_template('register.html', form=form)


if __name__ == "__main__":
    app.run(debug=True)