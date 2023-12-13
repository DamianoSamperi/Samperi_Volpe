import sqlite3

#forse tutto ciò si deve fare all'interno della funzione, vedi
conn = sqlite3.connect('users.db')

# Creazione di un cursore per eseguire le query SQL
cursor = conn.cursor()

# Creazione di una tabella di esempio
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
    
    # Commit delle modifiche e chiusura della connessione
    conn.commit()
    conn.close()

def get_client():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return users