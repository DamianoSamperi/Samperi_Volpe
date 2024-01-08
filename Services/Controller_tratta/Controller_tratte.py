import socket
import json
import sqlite3
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

try:
    conn=sqlite3.connect('controllertratte.db',check_same_thread=False)
    #conn1 = sqlite3.connect('tratte_salvate.db')
    #conn2 = sqlite3.connect('aeroporti_salvati.db')

    # Creazione di un cursore per eseguire le query SQL
    #cursor1 = conn1.cursor()
    #cursor2 = conn2.cursor()
    cursor=conn.cursor()
except sqlite3.Error as e:
    print(f"Errore durante la connessione al database: {e}")

try:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tratte_salvate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origine TEXT NOT NULL,
            destinazione TEXT NOT NULL,
            adulti INTEGER
        )
    ''') #tu avevi messo tratte
except sqlite3.Error as e:
    print(f"Errore durante l'esecuzione della query: {e}")

try:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aeroporti_salvati (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origine TEXT NOT NULL
        )
    ''') #tu avevi messo aeroporti
except sqlite3.Error as e:
    print(f"Errore durante l'esecuzione della query: {e}")

    
def leggi_database():
    try:
        # Esegui una query SQL
        cursor.execute("SELECT * FROM tratte_salvate")
        risultati = cursor.fetchall()
        cursor.execute("SELECT * FROM aeroporti_salvati")
        risultati2 = cursor.fetchall()

    except sqlite3.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")


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
        print(f"Errore durante l'esecuzione della query: {e}")
        return "error"



    # Chiudi la connessione
    # conn1.close()

    # Inizializza un array vuoto
    tratte = []

    # Itera sui risultati e aggiungi ogni tupla all'array come stringa
    for tupla in risultati:
        tratte.append({"origine": tupla[1] , "destinazione" : tupla[2], "adulti": tupla[3]}) #TO_DO Damiano credo sia giusto ma vedi tu


    # Stampa l'array di stringhe
    return tratte

def leggi_database_aeroporti():
    try:
        # Esegui una query SQL
        cursor.execute("SELECT * FROM aeroporti_salvati")

        # Ottieni i risultati
        risultati = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
        return "error"


    # Chiudi la connessione
    # conn1.close()

    # Inizializza un array vuoto
    aeroporti = []

    # Itera sui risultati e aggiungi ogni tupla all'array come stringa
    for tupla in risultati:
        aeroporti.append({"origine": tupla[1] })

    # Stampa l'array di stringhe
    return aeroporti

def scrivi_database_tratte(data):
    try:
        # Prepara la query SQL
        query = "SELECT COUNT(*) FROM tratte_salvate WHERE origine = ? AND destinazione = ? AND adulti= ?" #aggiunti adulti
    

        # Esegui la query SQL con i valori passati come parametri
        cursor.execute(query, (data['origine'], data['destinazione'], data['adulti']))
        count = cursor.fetchone()
        
        # Esegui il commit delle modifiche
    except sqlite3.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
        return e
    print("Count ",count[0])
    if count[0]==0:
        try:
            query = "INSERT INTO tratte_salvate ( origine, destinazione, adulti) VALUES (?, ?, ?)" #aggiunti adulti
            cursor.execute(query, (data['origine'], data['destinazione'], data['adulti']))
            conn.commit()
            return 'ok'
        except sqlite3.Error as e:
            print(f"Errore durante l'esecuzione della query: {e}")
            return e
    else:
        try:
            query = "DELETE FROM tratte_salvate WHERE origine = ? AND destinazione = ? AND adulti= ?" #aggiunti adulti
            cursor.execute(query, (data['origine'], data['destinazione'], data['adulti']))
            conn.commit()
            return 'ok'
        except sqlite3.Error as e:
            print(f"Errore durante l'esecuzione della query: {e}")
            return e

    # Chiudi la connessione
    #conn.close()

def scrivi_database_aeroporti(data):
    try:
        # Prepara la query SQL
        query = "SELECT COUNT(*) FROM aeroporti_salvati WHERE origine = ?" 
    
        # Esegui la query SQL con i valori passati come parametri
        cursor.execute(query, (data['aeroporto'],)) 
        count = cursor.fetchone()

        # Esegui il commit delle modifiche
        conn.commit()
    except sqlite3.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
    if count[0] == 0:
        try:
            query = "INSERT INTO aeroporti_salvati ( origine) VALUES (? )" #TO_DO da modificare se vogliamo aggiungere adults
            cursor.execute(query, (data['aeroporto'],))
            conn.commit()
            return 'ok'
        except sqlite3.Error as e:
            print(f"Errore durante l'esecuzione della query: {e}")
            return e
    else:
        try:
            query = "DELETE FROM aeroporti_salvati WHERE origine = ?" #TO_DO da modificare se vogliamo aggiungere adults
            cursor.execute(query, (data['aeroporto'],))
            conn.commit()
            return 'ok'
        except sqlite3.Error as e:
            print(f"Errore durante l'esecuzione della query: {e}")
            return e

    # Chiudi la connessione
    #conn.close()

@app.route('/invio_Scraper', methods=['POST']) 
def comunicazione_Scraper():
    richiesta= request.json
    if richiesta['request']=='tratta':
        tratte= leggi_database_tratte()
        return tratte
    elif richiesta['request'] == 'aeroporto':
        aeroporti=leggi_database_aeroporti()
        return aeroporti
    return "error"

@app.route('/ricevi_tratte_usercontroller', methods=['POST']) 
def comunicazioneUser_tratte():
    tratta= request.json
    response = scrivi_database_tratte(tratta)
    # tratte= leggi_database_tratte()
    # response = requests.post('http://user_controller:5000/recuperodati_scraper', {'vet_tratte':tratte})
    return response

@app.route('/ricevi_aeroporto_usercontroller', methods=['POST']) 
def comunicazioneUser_aeroporto():
    aeroporto = request.json
    response = scrivi_database_aeroporti(aeroporto)
    # aeroporti=leggi_database_aeroporti()
    # response = requests.post('http://user_controller:5000/recuperodati_scraper', {'vet_aroporti':aeroporti})
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5002, debug=True, threaded=True)
