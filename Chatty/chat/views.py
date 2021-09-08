from flask import Blueprint, render_template, session, jsonify, request
from flask.globals import request
from .database import DataBase

views = Blueprint('views', __name__)

@views.route('/chat', methods=['GET', 'POST'])
def chat():
    return render_template('chat.html')

@views.route('/get_username', methods=['GET', 'POST'])
def get_name():
    data = {'name': ''}
    if 'name' in session:
        data = {'name': session['name']}
    return jsonify(data)

@views.route('/search_users')
def get_all_users():
    db = DataBase()
    data = db.get_users()
    db.commit()
    return jsonify(data)

@views.route('/search_users/<username>', methods=['GET', 'POST'])
def search_users(username):
    db = DataBase()
    data = db.get_one_user(username)
    db.commit()
    return jsonify(data)

@views.route('/add_friend', methods=['GET', 'POST'])
def add_friend():
    db = DataBase()
    sender = db.get_one_user(request.json.get('sender'))[0]
    recevier = db.get_one_user(request.json.get('receiver'))[0]
    db.add_friend(sender.get('id'), recevier.get('id'))
    db.commit()
    return jsonify('Added!')

@views.route('/get_friends/<username>', methods=['GET'])
def get_friends(username):
    db = DataBase()
    user = db.get_one_user(username)[0]
    data = db.get_friends(user.get('id'))
    db.commit()
    return jsonify(data)

@views.route('/get_messages_one_user', methods=['GET', 'POST'])
def get_messages_one_user():
    db = DataBase()
    data = db.get_messages_one_user(request.json['user1'], request.json['user2'])
    return jsonify(data)
