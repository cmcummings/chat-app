# app.py
from exceptions import InvalidLoginError

# Initialize flask
from flask import Flask, render_template, url_for, session, redirect, request, escape
app = Flask(__name__)
app.debug = True
app.secret_key = b'JPtUKpetQiyfzGpBS5SM' # yeah, i don't care. hack me

# Establish connection to the database
from database import Connection
db = Connection(app, 'localhost', 27017)

# Initialize chatlogger
from chatlog import Logger
logger = Logger('chat.log')



# Index, shows the chatrooms
@app.route('/')
def index():

    if 'username' not in session:
        return redirect(url_for('login'))
    
    rooms = db.get_rooms()
    return render_template('rooms.html', username=session['username'], rooms=rooms)


# Login page
@app.route('/login/', methods=['GET', 'POST'])
def login():

    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in {None, ""}:
            return redirect(url_for('login', error="nouser"))

        try:
            if db.validate_login(username, password):
                session['username'] = username
                return redirect(url_for('index'))
            else:
                return redirect(url_for('login', error='invalidlogin'))
        except InvalidLoginError:
            return redirect(url_for('login', error='invalidlogin'))

    if request.method == 'GET':
        error = request.args.get('error', '')
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
    return redirect(url_for('login'))


# Chatroom page
@app.route('/room/<name>')
def room(name=None):
    if 'username' not in session:
        return redirect(url_for('login'))
    if name is None:
        return redirect(url_for('index'))

    messages = db.get_messages(name)
    return render_template('room.html', username=session['username'], room=name, messages=messages)

# Message functions
@app.route('/send-message/', methods=['GET']) # Inserts the message into the database, then returns all the messages in a room
def send_message():
    room = request.args.get('room', '')
    author = session['username']
    content = request.args.get('msg', '')
    
    logger.add_entry(room, author, content)
    db.add_message(room, author, content)
    messages = db.get_messages(room)
    return render_template('messages.html', messages=messages)

@app.route('/get-messages/', methods=['GET']) # Returns all the messages in a room
def get_messages():
    room = request.args.get('room', '')
   
    messages = db.get_messages(room)
    return render_template('messages.html', messages=messages)




if __name__ == '__main__':
    app.run(host='0.0.0.0') # Run on local network