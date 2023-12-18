import sqlite3
from flask import Flask, request, jsonify
import json

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
    
    ''' URL del servizio Flask
    url = 'http://localhost:5000/api/tratte_usercontroller'
    # Dati da inviare con la richiesta POST
    payload = jsonify({'tratte': result})
    # Imposta l'intestazione della richiesta per indicare che stai inviando dati JSON
    headers = {'Content-Type': 'application/json'}
    # Invia la richiesta POST al servizio Flask
    response = request.post(url, data=json.dumps(payload), headers=headers) #forse era requests, vedi
    # Stampa la risposta ricevuta dal servizio
    print(response.status_code)
    print(response.json())'''

def get_aeroporti():
    cursor2.execute(" SELECT * from aeroporti")
    result=cursor2.fetchall()
    return result 

    '''# URL del servizio Flask
    url = 'http://localhost:5000/api/aeroporti_usercontroller'
    # Dati da inviare con la richiesta POST
    payload = jsonify({'aeroporti': result})
    # Imposta l'intestazione della richiesta per indicare che stai inviando dati JSON
    headers = {'Content-Type': 'application/json'}
    # Invia la richiesta POST al servizio Flask
    response = request.post(url, data=json.dumps(payload), headers=headers) #forse era requests, vedi
    # Stampa la risposta ricevuta dal servizio
    print(response.status_code)
    print(response.json())'''

def get_users_by_tratta_and_budget(origine,destinazione,prezzo):
    cursor1.execute(" SELECT user_id FROM tratte WHERE origine=" + origine +
    "AND destinazione= " + destinazione + "AND budget>=" + prezzo)
    return cursor1.fetchall()

def get_users_by_aeroporto(aeroporto):
    cursor2.execute(" SELECT user_id FROM aeroporti WHERE origine=" + aeroporto)
    return cursor2.fetchall()

#la chiamo solo se crasha qualcosa 
def crash():
    conn1.close()
    conn2.close()

#TO-DO PROVA FLASK ----------------------------------------------------------------------
'''def get_tratte_flask():
    cursor1.execute(" SELECT * from tratte")
    result=cursor1.fetchall()'''
    