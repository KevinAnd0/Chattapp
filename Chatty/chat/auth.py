from flask import Blueprint, render_template, redirect, url_for, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from .database import DataBase
auth = Blueprint('auth', __name__)


@auth.route('/', methods=['GET', 'POST'])
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = DataBase()
        user = db.get_one_user(username=username)[0]
        db.commit()
        if user:
            if check_password_hash(user.get('password'), password):
                session['name'] = username
                return redirect(url_for('views.chat'))
            else:
                return jsonify("Password doesn't match")
        else:
            return jsonify('No user by that name!')

    return render_template("login.html")


@auth.route('/register', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password1')
        db = DataBase()
        username_exists = db.get_one_user(username)
        if username_exists:
            return jsonify('Username already exists')
        else:
            db.create_user(username=username, password=generate_password_hash(password, method='sha256'))
            db.commit()
            return redirect(url_for('views.chat'))
    return render_template('signup.html')


@auth.route('/logout')
def logout():   
    return redirect(url_for('auth.login'))