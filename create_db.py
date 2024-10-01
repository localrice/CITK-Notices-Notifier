import sqlite3 

conn = sqlite3.connect('notices.db')
cursor = conn.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        title TEXT,
        link TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT UNIQUE
    )
''')

conn.commit()
conn.close()
