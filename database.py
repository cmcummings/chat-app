# database.py
import pymongo
from datetime import datetime
import bcrypt
from exceptions import InvalidLoginError, UsernameTakenError


class Connection:
    """A connection to the database."""

    def __init__(self, app, host, port):
        self.app = app
        self.client = pymongo.MongoClient(host, port)
    
        self.db = self.client['chat-app']
        self.messages = self.db['messages']
        self.rooms = self.db['rooms']
        self.users = self.db['users']

    # Message functions
    def get_messages(self, room, max=50):
        """Retrieves the messages from a chatroom."""
        results = self.messages.find({'room': room}, limit=max) # Get the messages
        results = results.sort('date', pymongo.ASCENDING) # Sort by date in ascending order so later messages are at the bottom
        return results

    def add_message(self, room, author, content):
        """Adds a message to the database."""
        if self.room_exists(room):
            message = {
                'room': room,
                'author': author,
                'date': datetime.now(),
                'content': content
            }
            self.messages.insert_one(message)
            return True # Insertion was successful
        else:
            self.app.logger.warning('A message was attempted to be sent to the invalid room: %s', room)
            return False # Insertion was unsuccessful

    # Room functions
    def room_exists(self, name):
        """Checks if a room exists."""
        if self.rooms.count_documents({'name': name}) > 0:
            return True
        return False

    def get_rooms(self, max=50):
        """Gets all the existing rooms."""
        results = self.rooms.find(limit=max)
        return results

    def create_room(self, name):
        """Creates a room."""
        if not self.room_exists(name):
            self.rooms.insert_one({'name': name})

    # User functions
    def validate_login(self, username, password):
        """Checks if the login credentials are valid."""
        # Get user object from db
        user = self.users.find_one({'username': username})
        # Check if user exists
        if user is not None:
            # Check password
            hashed_pw = user['password']
            if bcrypt.hashpw(password.encode('utf-8'), hashed_pw) == hashed_pw:
                return True
            else:
                return False
        else:
            raise InvalidLoginError("The user doesn't exist.")

    def create_user(self, username, password):
        """Creates a user. Takes in the user's name and plaintext (unhashed) password."""
        # Check if the username is taken
        if self.users.count_documents({'username': username}) == 0:
            # Create the user
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user = {
                'username': username,
                'password': hashed_pw
            }
            self.users.insert_one(user)
        else:
            raise UsernameTakenError("The username is taken.")