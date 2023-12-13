import sqlite3

conn = sqlite3.connect('tratte.db')
conn= sqlite3.connect('aeroporti.db')

# Creazione di un cursore per eseguire le query SQL
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tratte (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        origine TEXT NOT NULL,
        destinazione TEXT NOT NULL,
        budget INTEGER
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS aeroporti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        origine TEXT NOT NULL,
        budget INTEGER
    )
''')

def inserisci_tratta(user_id,origine,destinazione,budget):
    cursor.execute('''
    INSERT INTO tratte (user_id, origine, destinazione, budget)
    VALUES (?, ?, ?, ?)
    ''', (user_id, origine, destinazione, budget))
    
    # Commit delle modifiche e chiusura della connessione
    conn.commit()
    conn.close()
    return

def inserisci_aeroporto(user_id,origine,budget):
    cursor.execute('''
    INSERT INTO tratte (user_id, origine, budget)
    VALUES (?, ?, ?, ?)
    ''', (user_id, origine, budget))
    
    # Commit delle modifiche e chiusura della connessione
    conn.commit()
    conn.close()
    return