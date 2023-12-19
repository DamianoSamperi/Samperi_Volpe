import socket
import json
import sqlite3
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)


conn1 = sqlite3.connect('tratte_salvate.db')
conn2 = sqlite3.connect('aeroporti_salvati.db')

# Creazione di un cursore per eseguire le query SQL
cursor1 = conn1.cursor()
cursor2 = conn2.cursor()
cursor1.execute('''
    CREATE TABLE IF NOT EXISTS tratte (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        origine TEXT NOT NULL,
        destinazione TEXT NOT NULL,
        budget INTEGER
    )
''')

cursor2.execute('''
    CREATE TABLE IF NOT EXISTS aeroporti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        origine TEXT NOT NULL,
        budget INTEGER
    )
''')

#questo se utilizziamo il database Rules
def leggi_database():
    # #conn = connessione a database
    # conn = sqlite3.connect('tratte_salvate.db')
    # # Crea un cursore
    # cur = conn.cursor()

    # Esegui una query SQL
    cursor1.execute("SELECT * FROM tratte_salvate")
    cursor2.execute("SELECT * FROM aeroporti_salvati")

    # Ottieni i risultati
    risultati = cursor1.fetchall()
    risultati2 = cursor2.fetchall()


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
def scrivi_database_tratte(data):
    #conn = connessione al database

    # Crea un cursore
    # cur = conn.cursor()

    # Prepara la query SQL
    query = "INSERT INTO tratte_salvate ( origine, destinazione , budget) VALUES (?, ?, ? )" #TO_DO da modificare se vogliamo aggiungere adults

    # Esegui la query SQL con i valori passati come parametri
    cursor1.execute(query, (data[0], data[1], data[2]))

    # Esegui il commit delle modifiche
    conn1.commit()

    # Chiudi la connessione
    #conn.close()
def scrivi_database_aeroporti(data):
    #conn = connessione al database

    # Crea un cursore
    # cur = conn.cursor()

    # Prepara la query SQL
    query = "INSERT INTO tratte_salvate ( origine, budget) VALUES (?, ? )" #TO_DO da modificare se vogliamo aggiungere adults

    # Esegui la query SQL con i valori passati come parametri
    cursor2.execute(query, (data[0], data[1]))

    # Esegui il commit delle modifiche
    conn2.commit()

    # Chiudi la connessione
    #conn.close()


def comunicazionepost():
    tratte = leggi_database()
    response = requests.post('http://localhost:5000/recuperodati_scraper', {'vet_tratte':'tratte'})
    # return response.text   

#TO_DO Elena le comunicazioni di user controller devono inviarla qui
@app.route('/inviodati_controllo', methods=['POST']) 
def comunicazioneUser():
    #incomes.append(request.get_json())
    tratte, aeroporti = request.form['vet_tratte','vet_aeroporti']
    scrivi_database_tratte(tratte)
    scrivi_database_aeroporti(aeroporti)
    # return '', 204    
def comunicazionesocket():
    # Crea un socket TCP/IP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Associa il socket a una porta
    server_address = ('localhost', 12345)
    sock.bind(server_address)

    # Ascolta le connessioni in arrivo
    sock.listen(1)

    while True:
        # Attende una connessione
        print('In attesa di una connessione...')
        connection, client_address = sock.accept()

        try:
            print('Connessione da', client_address)

            # Riceve i dati in piccoli segmenti
            # data = connection.recv(16)
            # print('Ricevuto {!r}'.format(data))

            # Invia i dati
            # if data:
            print('Invio del vettore allo Scraper')
            vector = leggi_database()
            connection.sendall(vector.encode('utf-8'))

        finally:
            # Pulisce la connessione
            connection.close() 
     