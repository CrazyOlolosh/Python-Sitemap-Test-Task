import sqlite3


class Database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS sitemap
                           (url TEXT, time_consumed REAL, links_found INTEGER, result_filename TEXT)''')
        self.conn.commit()

    def insert_record(self, url, time_consumed, links_found, result_filename):
        self.cursor.execute("INSERT INTO sitemap VALUES (?, ?, ?, ?)",
                            (url, time_consumed, links_found, result_filename))
        self.conn.commit()

    def close(self):
        self.conn.close()
