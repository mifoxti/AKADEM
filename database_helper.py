import sqlite3


# Функция для создания таблицы тусовок
def create_party_table():
    try:
        conn = sqlite3.connect('data/data.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS party (
                ID INTEGER PRIMARY KEY,
                Title TEXT,
                Date TEXT,
                Cost TEXT,
                Image TEXT,
                Description TEXT            
            )
        ''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(e)


# Функция для создания таблицы-связей
def create_ticket_party_user_table():
    try:
        conn = sqlite3.connect('data/data.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS ticket_party_user (
                ticket_id INTEGER,
                party_id INTEGER,
                user_id INTEGER
            )
        ''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(e)


# Функция для создания таблицы билетов
def create_ticket_table():
    try:
        conn = sqlite3.connect('data/data.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS ticket (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                level INTEGER
        )''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(e)


# Функция для создания таблицы пользователей
def create_user_table():
    try:
        conn = sqlite3.connect('data/data.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS user (
                ID INTEGER PRIMARY KEY,
                Name TEXT,
                Surn TEXT,
                Nick TEXT
        )''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(e)


# Функция поиска данных юзера в бд
def find_user(id):
    try:
        conn = sqlite3.connect('data/data.db')
        c = conn.cursor()
        c.execute('''SELECT * FROM user WHERE ID=?''', (id,))
        user_data = c.fetchone()
        conn.commit()
        conn.close()
        return user_data
    except sqlite3.Error as e:
        print(e)


# Функция создания записи нового юзера в бд
def register_user(id, name, surname, nick):
    try:
        conn = sqlite3.connect('data/data.db')
        c = conn.cursor()
        c.execute('''INSERT INTO user (
        ID, Name, Surn, Nick) VALUES (?, ?, ?, ?)''',
                  (id, name, surname, nick))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(e)


def generate_ticket(level):
    try:
        conn = sqlite3.connect('data/data.db')
        c = conn.cursor()
        c.execute('''INSERT INTO ticket (
        level) VALUES (?)''',
                  (level,))
        ticket_id = c.lastrowid
        conn.commit()
        conn.close()
        return ticket_id
    except sqlite3.Error as e:
        print(e)


def generate_party(title, date, description, image):
    try:
        conn = sqlite3.connect('data/data.db')
        c = conn.cursor()
        c.execute('''
        INSERT INTO party (Title, Date, Description, Image) VALUES (?, ?, ?, ?)
        ''', (title, date, description, image))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(e)


def get_events():
    try:
        conn = sqlite3.connect('data/data.db')
        c = conn.cursor()
        c.execute('''
        SELECT * FROM party
        ''')
        events = c.fetchall()
        conn.commit()
        conn.close()
        return events
    except sqlite3.Error as e:
        print(e)


def find_event_by_id(id):
    try:
        conn = sqlite3.connect('data/data.db')
        c = conn.cursor()
        c.execute('''SELECT * FROM party WHERE ID=?''', (id,))
        event = c.fetchone()
        conn.commit()
        conn.close()
        return event
    except sqlite3.Error as e:
        print(e)


def generate_ticket_party_user_aspect(ticket_id, party_id, user_id):
    try:
        conn = sqlite3.connect('data/data.db')
        c = conn.cursor()
        c.execute('''
        INSERT INTO ticket_party_user (ticket_id, party_id, user_id) VALUES (?, ?, ?)''',
                  (ticket_id, party_id, user_id))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(e)


def find_ticket_by_user_id(user_id):
    try:
        conn = sqlite3.connect('data/data.db')
        c = conn.cursor()
        c.execute('''
        SELECT * FROM ticket_party_user WHERE user_id=?''', (user_id,))
        tickets = c.fetchall()
        conn.commit()
        conn.close()
        return tickets
    except sqlite3.Error as e:
        print(e)


def find_ticket_by_id(ticket_id):
    try:
        conn = sqlite3.connect('data/data.db')
        c = conn.cursor()
        c.execute('''
        SELECT * FROM ticket WHERE ID=?''', (ticket_id,))
        tickets = c.fetchone()
        conn.commit()
        conn.close()
        return tickets
    except sqlite3.Error as e:
        print(e)