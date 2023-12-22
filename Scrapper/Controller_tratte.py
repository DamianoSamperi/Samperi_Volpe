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
        query = "REPLACE INTO tratte_salvate ( origine, destinazione ) VALUES (?, ? )" #TO_DO da modificare se vogliamo aggiungere adults
        #TO-DO replace dovrebbe inserirlo se manca e sostituirlo se uguale
    

        # Esegui la query SQL con i valori passati come parametri
        cursor1.execute(query, (data[0], data[1]))

        # Esegui il commit delle modifiche
        conn1.commit()
    except sqlite3.Error as e:
        print("Errore durante l'esecuzione della query: {e}")

    # Chiudi la connessione
    #conn.close()

def scrivi_database_aeroporti(data):
    try:
        # Prepara la query SQL
        query = "REPLACE INTO tratte_salvate ( origine) VALUES (? )" #TO_DO da modificare se vogliamo aggiungere adults
        #TO-DO replace dovrebbe inserirlo se manca e sostituirlo se uguale
    
        # Esegui la query SQL con i valori passati come parametri
        cursor2.execute(query, (data[0]))

        # Esegui il commit delle modifiche
        conn2.commit()
    except sqlite3.Error as e:
        print("Errore durante l'esecuzione della query: {e}")

    # Chiudi la connessione
    #conn.close()

#TO_DO per fare questo dovrei inserirlo in un ciclo while con un timer di 24 ore, invece ho deciso di inviarle ogni volta che ha una comunicazione con l'user controller
def comunicazionepost():
    tratte ,aeroporti = leggi_database()
    response = requests.post('http://localhost:5000/recuperodati_scraper', {'vet_tratte':tratte, 'vet_aroporti':aeroporti})
    # return response.text   

#TO_DO Elena le comunicazioni di user controller devono inviarla qui
@app.route('/ricevi_tratte_usercontroller', methods=['POST']) 
def comunicazioneUser():
    tratta= request.json
    scrivi_database_tratte(tratta)
    tratte= leggi_database_tratte()
    response = requests.post('http://localhost:5000/recuperodati_scraper', {'vet_tratte':tratte})

    # return '', 204    
@app.route('/ricevi_aeroporto_usercontroller', methods=['POST']) 
def comunicazioneUser():
    aeroporto = request.json
    scrivi_database_aeroporti(aeroporto)
    aeroporti=leggi_database_aeroporti()
    response = requests.post('http://localhost:5000/recuperodati_scraper', {'vet_aroporti':aeroporti})

    # return '', 204   
     

