# Script to make a new user

from flask import Flask
app = Flask(__name__)
app.debug = True
app.secret_key = b'JPtUKpetQiyfzGpBS5SM' # yeah, i don't care. hack me

from database import Connection
db = Connection(app, 'localhost', 27017)

db.create_user("user2", "test2") # Make new user