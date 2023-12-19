import sqlite3

conn = sqlite3.connect('users.db')

# Creazione di un cursore per eseguire le query SQL
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cognome TEXT NOT NULL,
        email TEXT NOT NULL
    )
''')

def inserisci_client(nome,cognome,email):
    cursor.execute('''
    INSERT INTO users (nome, cognome, email)
    VALUES (?, ?, ?)
    ''', (nome, cognome, email))

    conn.commit()

def get_clients():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return users

'''def get_id_by_email(email):
    id=cursor.execute("SELECT user_id FROM users WHERE email=" + email)
    return id'''

def control_client(email):
    cursor.execute("SELECT user_id FROM users WHERE email=" + email)
    result=cursor.fetchall()
    if result != None:
        return result
    else:
        return False

#la chiamo solo se crasha qualcosa
def crash():
    conn.close()