# app.py

# Initialize flask
from flask import Flask, render_template, url_for, session, redirect, request, escape
app = Flask(__name__)
app.debug = True
app.secret_key = b'JPtUKpetQiyfzGpBS5SM' # yeah, i don't care. hack me

# Establish connection to the database
from database import Connection
db = Connection(app, 'localhost', 27017)



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
        if request.form['username'] in {None, ""}:
            return redirect(url_for('login', error="nouser"))
        session['username'] = request.form['username']
        return redirect(url_for('index'))

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

    messages = db.get_messages(name)
    return render_template('room.html', username=session['username'], room=name, messages=messages)

@app.route('/send-message/', methods=['GET'])
def send_message():
    room = request.args.get('room', '')
    author = session['username']
    content = request.args.get('msg', '')
    
    db.add_message(room, author, content)
    return render_template('messages.html', messages=db.get_messages(room))

@app.route('/get-messages/', methods=['GET'])
def get_messages():
    room = request.args.get('room', '')
   
    messages = db.get_messages(room)
    return render_template('messages.html', messages=db.get_messages(room))




if __name__ == '__main__':
    app.run()