from flask import Flask,render_template, request, session, Response, redirect
from database import connector
from model import entities
import json
import time
import pusher

db = connector.Manager()
engine = db.createEngine()

app = Flask(__name__)

pusher_client = pusher.Pusher(
  app_id='804757',
  key='ea1510aece55b0dd085a',
  secret='902ccddbae67ee224d7d',
  cluster='us2',
  ssl=True
)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/messages', methods=['GET', 'POST'])
def get_crud_messages():
    session = db.getSession(engine)
    dbResponse = session.query(entities.Message)
    data = []
    for user in dbResponse:
        data.append(user)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')


@app.route('/messages', methods=['DELETE'])
def delete_crud_messages():
    id = request.form['key']
    session = db.getSession(engine)
    messages = session.query(entities.Message).filter(entities.Message.id == id)
    for message in messages:
        session.delete(message)
    session.commit()
    return "Deleted Message"


@app.route('/static/<content>')
def static_content(content):
    return render_template(content)


@app.route('/users', methods=['GET'])
def get_users():
    session = db.getSession(engine)
    dbResponse = session.query(entities.User)
    data = []
    for user in dbResponse:
        data.append(user)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')


@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    db_session = db.getSession(engine)
    users = db_session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return Response(js, status=200, mimetype='application/json')

    message = {'status': 404, 'message': 'Not Found'}
    return Response(message, status=404, mimetype='application/json')


@app.route('/create_test_users', methods=['GET'])
def create_test_users():
    db_session = db.getSession(engine)
    user = entities.User(name="David", fullname="Lazo", password="1234", username="qwerty")
    db_session.add(user)
    db_session.commit()
    return "Test user created!"


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
    c =json.loads(request.form['values'])
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


@app.route('/authenticate', methods=["POST"])
def authenticate():
    time.sleep(1)
    message = json.loads(request.data)
    username = message['username']
    password = message['password']
    # 2. look in database
    db_session = db.getSession(engine)
    try:
        user = db_session.query(entities.User).filter(entities.User.username == username).filter(entities.User.password == password).one()
        session['logged_user'] = user.id
        message = {'message': 'Authorized'}
        return Response(message, status=200, mimetype='application/json')
    except Exception:
        message = {'message': 'Unauthorized'}
        return Response(message, status=401, mimetype='application/json')


@app.route('/current', methods=["GET"])
def current_user():
    db_session = db.getSession(engine)
    user = db_session.query(entities.User).filter(
        entities.User.id == session['logged_user']
        ).first()
    return Response(json.dumps(
            user,
            cls=connector.AlchemyEncoder),
            mimetype='application/json'
        )


@app.route('/logout', methods=["GET"])
def logout():
    session.clear()
    return render_template('index.html')


@app.route('/messages/<user_from_id>/<user_to_id>', methods = ['GET'])
def get_messages(user_from_id, user_to_id):
    db_session = db.getSession(engine)
    messages = db_session.query(entities.Message).filter(
        entities.Message.user_from_id == user_from_id).filter(
        entities.Message.user_to_id == user_to_id
    )
    messages_2 = db_session.query(entities.Message).filter(
        entities.Message.user_from_id == user_to_id).filter(
        entities.Message.user_to_id == user_from_id
    )
    data = []
    for message in messages:
        data.append(message)
    for message_2 in messages_2:
        data.append(message_2)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')


@app.route('/gabriel/messages', methods = ["POST"])
def create_message():
    data = json.loads(request.data)
    user_to_id = data['user_to_id']
    user_from_id = data['user_from_id']
    content = data['content']

    message = entities.Message(user_to_id=user_to_id, user_from_id=user_from_id, content=content)

    # 2. Save in database
    db_session = db.getSession(engine)
    db_session.add(message)
    db_session.commit()

    pusher_client.trigger('my-channel', 'my-event', {'user_from_id': user_from_id, 'user_to_id': user_to_id,
                                                     'content': content})
    response = {'message': 'created'}
    return Response(json.dumps(response, cls=connector.AlchemyEncoder), status=200, mimetype='application/json')


if __name__ == '__main__':
    app.secret_key = ".."
    app.run(port=5000, threaded=True, host='127.0.0.1')
