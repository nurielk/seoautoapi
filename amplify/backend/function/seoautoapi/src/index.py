import awsgi
import boto3
import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from uuid import uuid4

#installation for storing the username
from flask import Flask, render_template, url_for, redirect



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

