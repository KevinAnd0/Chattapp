import sqlite3
from sqlite3 import Error
from datetime import datetime


class DataBase:
    def __init__(self):
        self.conn = sqlite3.connect('chat.db')
        self.conn.row_factory = self.make_dicts
        self.cursor = self.conn.cursor()
        self.create_user_table()
        self.create_message_table()
        self.create_friends_table()

    def commit(self):
        self.conn.commit()
        self.conn.close()

    def make_dicts(self, cursor, row):
        return dict((cursor.description[idx][0], value)
            for idx, value in enumerate(row))

    def create_user_table(self):
        query = '''CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, 
                    username TEXT UNIQUE, 
                    password TEXT, 
                    online BOOLEAN,
                    socket_id TEXT UNIQUE
                    )'''
        self.cursor.execute(query)

    def create_message_table(self):
        query = '''CREATE TABLE IF NOT EXISTS messages(
                    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, 
                    message TEXT, 
                    sender INTEGER, 
                    time Date,
                    FOREIGN KEY(sender) REFERENCES users(id)
                    )'''
        self.cursor.execute(query)

    def create_friends_table(self):
        query = '''CREATE TABLE IF NOT EXISTS friends(
                    user1 INTEGER, 
                    user2 INTEGER,
                    FOREIGN KEY(user1) REFERENCES users(id)
                    FOREIGN KEY(user2) REFERENCES users(id)
                    )'''
        self.cursor.execute(query)

    def create_room_table(self):
        query = '''CREATE TABLE IF NOT EXISTS users(
                    room_id INTEGER, 
                    user_id INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                    )'''
        self.cursor.execute(query)

    def create_user(self, username, password, id=None, online=True, socket_id=None):
        query = 'INSERT INTO users VALUES (?, ?, ?, ?, ?)'
        self.cursor.execute(query, (id, username, password, online, socket_id))

    def get_users(self, username=None):
        if not username:
            query = 'SELECT * FROM users'
            self.cursor.execute(query)
        else:
            query = 'SELECT * FROM users WHERE username = ?'
            self.cursor.execute(query, (username,))
        return self.cursor.fetchall()

    def get_one_user(self, username=None):
        return self.get_users(username=username)

    def update_user(self, online, socket_id, username):
        query = "UPDATE users SET online = ?, socket_id = ? WHERE username = ?"
        self.cursor.execute(query, (online, socket_id, username))

    def create_message(self, message, sender, time, id=None):
        query = 'INSERT INTO messages VALUES (?, ?, ?, ?)'
        self.cursor.execute(query, (id, message, sender, time))
        
    def add_friend(self, sender_id, recevier_id):
        query = 'INSERT INTO friends VALUES (? ,?)'
        self.cursor.execute(query, (sender_id, recevier_id))
        query = 'INSERT INTO friends VALUES (? ,?)'
        self.cursor.execute(query, (recevier_id, sender_id))

    def get_friends(self, user_id):
        query = '''SELECT users.username, users.online, users.socket_id
                    FROM users
                    JOIN friends
                    ON friends.user2 = users.id
                    WHERE friends.user1 = ?'''
        self.cursor.execute(query, (user_id,))
        return self.cursor.fetchall()

    def get_messages_one_user(self, user1, user2):
        query = '''SELECT *
                    FROM messages
                    WHERE sender in (?, ?)
                    ORDER BY time desc
                    '''
        self.cursor.execute(query, (user1, user2,))
        return self.cursor.fetchall()