import socket
import json
import sqlite3
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

try:
    conn=sqlite3.connect('voli.db')
    #conn1 = sqlite3.connect('tratte_salvate.db')
    #conn2 = sqlite3.connect('aeroporti_salvati.db')

    # Creazione di un cursore per eseguire le query SQL
    #cursor1 = conn1.cursor()
    #cursor2 = conn2.cursor()
    cursor=conn.cursor()
except sqlite3.Error as e:
    print("Errore durante la connessione al database: {e}")

try:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tratte_salvate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origine TEXT NOT NULL,
            destinazione TEXT NOT NULL,
            budget INTEGER
        )
    ''') #tu avevi messo tratte
except sqlite3.Error as e:
    print("Errore durante l'esecuzione della query: {e}")

try:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aeroporti_salvati (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origine TEXT NOT NULL,
            budget INTEGER
        )
    ''') #tu avevi messo aeroporti
except sqlite3.Error as e:
    print("Errore durante l'esecuzione della query: {e}")
    
def leggi_database():
    try:
        # Esegui una query SQL
        cursor.execute("SELECT * FROM tratte_salvate")
        cursor.execute("SELECT * FROM aeroporti_salvati")

        # Ottieni i risultati
        risultati = cursor.fetchall()
        risultati2 = cursor.fetchall()
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
        cursor.execute("SELECT * FROM tratte_salvate")

        # Ottieni i risultati
        risultati = cursor.fetchall()
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
        cursor.execute("SELECT * FROM aeroporti_salvati")

        # Ottieni i risultati
        risultati = cursor.fetchall()
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
        cursor.execute(query, (data[0], data[1]))
        count = cursor.fetchall()
        
        # Esegui il commit delle modifiche
    except sqlite3.Error as e:
        print("Errore durante l'esecuzione della query: {e}")
    if count==0:
        try:
            query = "INSERT INTO tratte_salvate ( origine, destinazione ) VALUES (?, ? )" #TO_DO da modificare se vogliamo aggiungere adults
            cursor.execute(query, (data[0], data[1]))
            conn.commit()
        except sqlite3.Error as e:
            print("Errore durante l'esecuzione della query: {e}")
    else:
        try:
            query = "DELETE FROM tratte_salvate WHERE origine = ? AND destinazione = ?" #TO_DO da modificare se vogliamo aggiungere adults
            cursor.execute(query, (data[0], data[1]))
            conn.commit()
        except sqlite3.Error as e:
            print("Errore durante l'esecuzione della query: {e}")

    # Chiudi la connessione
    #conn.close()

def scrivi_database_aeroporti(data):
    try:
        # Prepara la query SQL
        query = "SELECT COUNT(*) FROM aeroporti_salvati WHERE origine = ?" 
    
        # Esegui la query SQL con i valori passati come parametri
        cursor.execute(query, (data[0]))
        count = cursor.fetchall()

        # Esegui il commit delle modifiche
        conn.commit()
    except sqlite3.Error as e:
        print("Errore durante l'esecuzione della query: {e}")
    if count == 0:
        try:
            query = "INSERT INTO aeroporti_salvati ( origine) VALUES (? )" #TO_DO da modificare se vogliamo aggiungere adults
            cursor.execute(query, (data[0]))
            conn.commit()
        except sqlite3.Error as e:
            print("Errore durante l'esecuzione della query: {e}")
    else:
        try:
            query = "DELETE FROM aeroporti_salvati WHERE origine = ?" #TO_DO da modificare se vogliamo aggiungere adults
            cursor.execute(query, (data[0]))
            conn.commit()
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


@app.route('/ricevi_tratte_usercontroller', methods=['POST']) 
def comunicazioneUser():
    tratta= request.json
    scrivi_database_tratte(tratta)
    # tratte= leggi_database_tratte()
    # response = requests.post('http://localhost:5000/recuperodati_scraper', {'vet_tratte':tratte})

@app.route('/ricevi_aeroporto_usercontroller', methods=['POST']) 
def comunicazioneUser():
    aeroporto = request.json
    scrivi_database_aeroporti(aeroporto)
    # aeroporti=leggi_database_aeroporti()
    # response = requests.post('http://localhost:5000/recuperodati_scraper', {'vet_aroporti':aeroporti})

     

