import socket
import json
import sqlite3
from flask import Flask, jsonify, requests

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
#questo se vogliamo utilizzare un file
def leggi_file():
    tratte = []
    with open("tratte.txt", 'r') as file:
        for riga in file:
            # tratte.append(estrai_valori("originLocationCode=","destinationLocationCode=",riga))
            # tratte.append(estrai_valori("destinationLocationCode=","departureDate=",riga))
            # tratte.append(estrai_valori("departureDate=","adults=",riga))
            # tratte.append(estrai_valori("adults=","",riga))
            tratte.append(riga.split())         
    return tratte
def estrai_valori(parola_inizio, parola_fine,riga):
    # matrice = []
    # with open("tratte.txt", 'r') as file:
    #     for riga in file:
            parole = riga.split()
            print(parole)
            try:
                indice_inizio = parole.index(parola_inizio) + 1
                indice_fine = parole.index(parola_fine)
            except ValueError as error:
                # continue
                raise error
            valori = parole[indice_inizio:indice_fine]
            return valori

def scrivi_file(data):
    with open("tratte.txt", 'a') as file:
        file.write(data)

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
    #TO-DO Damiano devi controllare se esiste già
    #in più non c'è bisogno del budget, devi salvare solo la tratta
    #budget serve solo all'elaboratore e lo prende da Rules

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
    #TO-DO Damiano devi controllare se esiste già
    #in più non c'è bisogno del budget, devi salvare solo l'aeroporto'
    #budget serve solo all'elaboratore e lo prende da Rules

    # Esegui la query SQL con i valori passati come parametri
    cursor2.execute(query, (data[0], data[1]))

    # Esegui il commit delle modifiche
    conn2.commit()

    # Chiudi la connessione
    #conn.close()

#TO-DO Damiano scusa l'ignoranza,ma questa non è la richiesta per riceverlo?
#non devi implementare qui l'invio?
@app.route('/inviodati_scraper', methods=['POST']) 
def comunicazionepost():
    tratte = leggi_database()
    response = requests.post('http://localhost:5000/recuperodati_scraper', tratte=tratte)
    return response.text   
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

#TO-DO forse è così che funziona, qui riceve le tratte e aeroporti da UserController
@app.route('/ricevi_tratte_usercontroller', methods=['POST'])
def receive_data():
    if requests.method == 'POST': #forse è request?
        data = requests.json
        scrivi_database_tratte(data) #TO-DO nella funzione devi controllare che non esista già nel db
        #result = {'message': 'Data received successfully', 'data': data}
        #return jsonify(result) 
    
@app.route('/ricevi_aeroporti_usercontroller', methods=['POST'])
def receive_data():
    if requests.method == 'POST': #forse è request?
        data = requests.json
        scrivi_database_aeroporti(data) #TO-DO nella funzione devi controllare che non esista già nel db
        #result = {'message': 'Data received successfully', 'data': data}
        #return jsonify(result) 
     