from flask import Flask, render_template, request, session, Response, redirect, url_for, jsonify
from flask_socketio import SocketIO, send
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database import connector
from model import entities
import time
import json

db = connector.Manager()
engine = db.createEngine()
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'secretkey'
socketio = SocketIO(app)


@login_manager.user_loader
def get_user(user_id):
    db_session = db.getSession(engine)
    return db_session.query(entities.User).filter_by(id=user_id).first()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/static/<content>')
def static_content(content):
    return render_template(content)


@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    db_session = db.getSession(engine)
    users = db_session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return Response(js, status=200, mimetype='application/json')

    message = {'status': 404, 'message': 'Not Found'}
    return Response(message, status=404, mimetype='application/json')


@app.route('/messages', methods=['GET', 'POST'])
def get_messages():
    session = db.getSession(engine)
    dbResponse = session.query(entities.Message)
    data = []
    for user in dbResponse:
        data.append(user)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')


@app.route('/create_test_messages', methods=['GET', 'POST'])
def create_test_message():
    db_session = db.getSession(engine)
    user_1 = db_session.query(entities.User).filter(entities.User.id == 6).first()
    user_2 = db_session.query(entities.User).filter(entities.User.id == 5).first()
    message = entities.Message(content='Hello!', user_from=user_1, user_to=user_2)
    db_session.add(message)
    db_session.commit()
    return "Test message created!"


@app.route('/messages', methods=['DELETE'])
def delete_message():
    id = request.form['key']
    session = db.getSession(engine)
    messages = session.query(entities.Message).filter(entities.Message.id == id)
    for message in messages:
        session.delete(message)
    session.commit()
    return "Deleted Message"


@app.route('/users', methods=['GET'])
def get_users():
    session = db.getSession(engine)
    dbResponse = session.query(entities.User)
    data = []
    for user in dbResponse:
        data.append(user)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')


@app.route('/users', methods=['POST'])
def create_user():
    c = json.loads(request.form['values'])
    user = entities.User(
        username=c['username'],
        name=c['name'],
        fullname=c['fullname'],
        password=c['password']
    )
    session = db.getSession(engine)
    session.add(user)
    session.commit()
    return 'Created User'


@app.route('/users', methods=['PUT'])
def update_user():
    session = db.getSession(engine)
    id = request.form['key']
    user = session.query(entities.User).filter(entities.User.id == id).first()
    c = json.loads(request.form['values'])
    for key in c.keys():
        setattr(user, key, c[key])
    session.add(user)
    session.commit()
    return 'Updated User'


@app.route('/users', methods=['DELETE'])
def delete_user():
    id = request.form['key']
    session = db.getSession(engine)
    messages = session.query(entities.User).filter(entities.User.id == id)
    for message in messages:
        session.delete(message)
    session.commit()
    return "Deleted Message"


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        db_session = db.getSession(engine)
        username = request.form['username']
        password = request.form['password']
        registered_user = db_session.query(entities.User).filter_by(username=username, password=password).first()
        if registered_user is None:
            error = 'Invalid Credentials. Please try again.'
        else:
            login_user(registered_user)
            return redirect(url_for('get_users_chat'))
    return render_template('login.html', error=error)


@app.route('/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    return render_template('/static/login')


@app.route('/chat/<user_id>', methods=['GET'])
@login_required
def get_chat_messages(user_id):
    db_session = db.getSession(engine)
    posts_1 = db_session.query(entities.Message).filter(entities.Message.user_from_id == current_user.id).filter(entities.Message.user_to_id == user_id)
    posts_2 = db_session.query(entities.Message).filter(entities.Message.user_to_id == current_user.id).filter(entities.Message.user_from_id == user_id)
    return render_template('chat.html', posts_1=posts_1, posts_2=posts_2)


@app.route('/chat/<user_id>', methods=['GET', 'POST'])
@login_required
def new_message(user_id):
    message = entities.Message(
        content=request.form['content'],
        user_from_id=current_user.id,
        user_to_id=user_id
    )
    session = db.getSession(engine)
    session.add(message)
    session.commit()
    posts_1 = session.query(entities.Message).filter(entities.Message.user_from_id == current_user.id).filter(entities.Message.user_to_id == user_id)
    posts_2 = session.query(entities.Message).filter(entities.Message.user_to_id == current_user.id).filter(entities.Message.user_from_id == user_id)
    return render_template('chat.html', posts_1=posts_1, posts_2=posts_2)


@app.route('/chat_users', methods=['GET', 'POST'])
@login_required
def get_users_chat():
    db_session = db.getSession(engine)
    posts = db_session.query(entities.User).filter(entities.User.id != current_user.id)
    return render_template('chat_users.html', posts=posts)


@socketio.on('message')
def handle_message(msg):
    send(msg, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, port=8080, host='127.0.0.1')
