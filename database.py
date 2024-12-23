
import sqlite3

class DatabaseHandler:
    def __init__(self, db_name="giveaway_bot.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS participants (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               username TEXT NOT NULL UNIQUE,
                               liked BOOLEAN,
                               commented BOOLEAN,
                               reposted BOOLEAN
                           )''')
        self.conn.commit()

    def add_or_update_participant(self, username, liked, commented, reposted):
        self.cursor.execute('''INSERT OR REPLACE INTO participants (username, liked, commented, reposted)
                               VALUES (?, ?, ?, ?)''', (username, liked, commented, reposted))
        self.conn.commit()

    def close(self):
        self.conn.close()
