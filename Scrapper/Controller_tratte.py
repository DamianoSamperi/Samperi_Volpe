import socket
import json
import sqlite3
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

try:
    conn1 = sqlite3.connect('tratte_salvate.db')
    conn2 = sqlite3.connect('aeroporti_salvati.db')

    # Creazione di un cursore per eseguire le query SQL
    cursor1 = conn1.cursor()
    cursor2 = conn2.cursor()
except sqlite3.Error as e:
    print("Errore durante la connessione al database: {e}")

try:
    cursor1.execute('''
        CREATE TABLE IF NOT EXISTS tratte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origine TEXT NOT NULL,
            destinazione TEXT NOT NULL,
            budget INTEGER
        )
    ''')
except sqlite3.Error as e:
    print("Errore durante l'esecuzione della query: {e}")

try:
    cursor2.execute('''
        CREATE TABLE IF NOT EXISTS aeroporti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origine TEXT NOT NULL,
            budget INTEGER
        )
    ''')
except sqlite3.Error as e:
    print("Errore durante l'esecuzione della query: {e}")
    
def leggi_database():
    try:
        # Esegui una query SQL
        cursor1.execute("SELECT * FROM tratte_salvate")
        cursor2.execute("SELECT * FROM aeroporti_salvati")

        # Ottieni i risultati
        risultati = cursor1.fetchall()
        risultati2 = cursor2.fetchall()
    except sqlite3.Error as e:
        print("Errore durante l'esecuzione della query: {e}")


    # Chiudi la connessione
    # conn1.close()

    # Inizializza un array vuoto
    tratte = []
    aeroporti = []

    # Itera sui risultati e aggiungi ogni tupla all'array come stringa
    for tupla in risultati:
        tratte.append(tupla)
    for tupla in risultati2:
        aeroporti.append(tupla)

    # Stampa l'array di stringhe
    return tratte,aeroporti

def leggi_database_tratte():
    try:
        # Esegui una query SQL
        cursor1.execute("SELECT * FROM tratte_salvate")

        # Ottieni i risultati
        risultati = cursor1.fetchall()
    except sqlite3.Error as e:
        print("Errore durante l'esecuzione della query: {e}")
        return "error"



    # Chiudi la connessione
    # conn1.close()

    # Inizializza un array vuoto
    tratte = []

    # Itera sui risultati e aggiungi ogni tupla all'array come stringa
    for tupla in risultati:
        tratte.append(tupla)


    # Stampa l'array di stringhe
    return tratte

def leggi_database_aeroporti():
    try:
        # Esegui una query SQL
        cursor2.execute("SELECT * FROM aeroporti_salvati")

        # Ottieni i risultati
        risultati = cursor2.fetchall()
    except sqlite3.Error as e:
        print("Errore durante l'esecuzione della query: {e}")
        return "error"


    # Chiudi la connessione
    # conn1.close()

    # Inizializza un array vuoto
    aeroporti = []

    # Itera sui risultati e aggiungi ogni tupla all'array come stringa
    for tupla in risultati:
        aeroporti.append(tupla)

    # Stampa l'array di stringhe
    return aeroporti

def scrivi_database_tratte(data):
    try:
        # Prepara la query SQL
        query = "SELECT COUNT(*) FROM tratte_salvate WHERE origine = ? AND destinazione = ?" #TO_DO da modificare se vogliamo aggiungere adults
    

        # Esegui la query SQL con i valori passati come parametri
        cursor1.execute(query, (data[0], data[1]))
        count = cursor1.fetchall()
        
        # Esegui il commit delle modifiche
    except sqlite3.Error as e:
        print("Errore durante l'esecuzione della query: {e}")
    if count==0:
        try:
            query = "INSERT INTO tratte_salvate ( origine, destinazione ) VALUES (?, ? )" #TO_DO da modificare se vogliamo aggiungere adults
            cursor1.execute(query, (data[0], data[1]))
            conn1.commit()
        except sqlite3.Error as e:
            print("Errore durante l'esecuzione della query: {e}")
    else:
        try:
            query = "DELETE FROM tratte_salvate WHERE origine = ? AND destinazione = ?" #TO_DO da modificare se vogliamo aggiungere adults
            cursor1.execute(query, (data[0], data[1]))
            conn1.commit()
        except sqlite3.Error as e:
            print("Errore durante l'esecuzione della query: {e}")

    # Chiudi la connessione
    #conn.close()

def scrivi_database_aeroporti(data):
    try:
        # Prepara la query SQL
        query = "SELECT COUNT(*) FROM aeroporti_salvati WHERE origine = ?" 
    
        # Esegui la query SQL con i valori passati come parametri
        cursor2.execute(query, (data[0]))
        count = cursor2.fetchall()

        # Esegui il commit delle modifiche
        conn2.commit()
    except sqlite3.Error as e:
        print("Errore durante l'esecuzione della query: {e}")
    if count == 0:
        try:
            query = "INSERT INTO aeroporti_salvati ( origine) VALUES (? )" #TO_DO da modificare se vogliamo aggiungere adults
            cursor2.execute(query, (data[0]))
            conn2.commit()
        except sqlite3.Error as e:
            print("Errore durante l'esecuzione della query: {e}")
    else:
        try:
            query = "DELETE FROM aeroporti_salvati WHERE origine = ?" #TO_DO da modificare se vogliamo aggiungere adults
            cursor2.execute(query, (data[0]))
            conn2.commit()
        except sqlite3.Error as e:
            print("Errore durante l'esecuzione della query: {e}")

    # Chiudi la connessione
    #conn.close()

#TO_DO oltre questo si possono inviare ogni volta che arriva un aggiornamento sulle tratte-aeroporti, bisogna considerare qual'è l'opzione migliore
@app.route('/invio_Scraper', methods=['POST']) 
def comunicazione_Scraper():
    richiesta= request.json
    if richiesta=='tratta':
        tratte= leggi_database_tratte()
        return tratte
    elif richiesta == 'aroporto':
        aeroporti=leggi_database_aeroporti()
        return aeroporti


# @app.route('/ricevi_tratte_usercontroller', methods=['POST']) 
# def comunicazioneUser():
#     tratta= request.json
#     scrivi_database_tratte(tratta)
#     tratte= leggi_database_tratte()
#     response = requests.post('http://localhost:5000/recuperodati_scraper', {'vet_tratte':tratte})

# @app.route('/ricevi_aeroporto_usercontroller', methods=['POST']) 
# def comunicazioneUser():
#     aeroporto = request.json
#     scrivi_database_aeroporti(aeroporto)
#     aeroporti=leggi_database_aeroporti()
#     response = requests.post('http://localhost:5000/recuperodati_scraper', {'vet_aroporti':aeroporti})

     

