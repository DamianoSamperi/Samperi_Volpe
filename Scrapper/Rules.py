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
    
    conn1.commit()

def inserisci_aeroporto(user_id,origine,budget):
    cursor2.execute('''
    INSERT INTO aeroporti (user_id, origine, budget)
    VALUES (?, ?, ?, ?)
    ''', (user_id, origine, budget))
 
    conn2.commit()

def get_tratte():
    cursor1.execute(" SELECT * from tratte")
    result=cursor1.fetchall()
    return result

def get_aeroporti():
    cursor2.execute(" SELECT * from aeroporti")
    result=cursor2.fetchall()
    return result

def get_users_by_tratta_and_budget(origine,destinazione,prezzo):
    cursor1.execute(" SELECT user_id FROM tratte WHERE origine=" + origine +
    "AND destinazione= " + destinazione + "AND budget>=" + prezzo)
    return cursor1.fetchall()

def get_users_by_aeroporto(aeroporto):
    cursor2.execute(" SELECT user_id FROM aeroporti WHERE origine=" + aeroporto)
    return cursor2.fetchall()

#farlo se crasha qualcosa
def chiusura_programma():
    conn1.close()
    conn2.close()