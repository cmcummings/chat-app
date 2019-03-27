# database.py
import pymongo
from datetime import datetime


class Connection:
    """A connection to the MongoDB database."""

    def __init__(self, app, host, port):
        self.app = app
        self.client = pymongo.MongoClient(host, port)

        self.chat_db = self.client['chat-app']
        self.messages = self.chat_db['messages']
        self.rooms = self.chat_db['rooms']

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
        if self.rooms.count_documents({'name': name}) > 0:
            return True
        return False

    def get_rooms(self, max=50):
        results = self.rooms.find(limit=max)
        return results

    # User functions
