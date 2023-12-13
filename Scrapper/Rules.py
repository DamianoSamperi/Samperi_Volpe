import sqlite3

conn1 = sqlite3.connect('tratte.db')
conn2 = sqlite3.connect('aeroporti.db')

# Creazione di un cursore per eseguire le query SQL
cursor1 = conn1.cursor()
cursor2 = conn2.cursor()

cursor1.execute('''
    CREATE TABLE IF NOT EXISTS tratte (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        origine TEXT NOT NULL,
        destinazione TEXT NOT NULL,
        budget INTEGER
    )
''')

cursor2.execute('''
    CREATE TABLE IF NOT EXISTS aeroporti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        origine TEXT NOT NULL,
        budget INTEGER
    )
''')

def inserisci_tratta(user_id,origine,destinazione,budget):
    cursor1.execute('''
    INSERT INTO tratte (user_id, origine, destinazione, budget)
    VALUES (?, ?, ?, ?)
    ''', (user_id, origine, destinazione, budget))
    
    # Commit delle modifiche e chiusura della connessione
    conn1.commit()
    return

def inserisci_aeroporto(user_id,origine,budget):
    cursor2.execute('''
    INSERT INTO aeroporti (user_id, origine, budget)
    VALUES (?, ?, ?, ?)
    ''', (user_id, origine, budget))
    
    # Commit delle modifiche e chiusura della connessione
    conn2.commit()
    return

#farlo se crasha qualcosa
#conn1.close()
#conn2.close()