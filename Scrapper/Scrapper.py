from msilib import Control
from amadeus import Client, ResponseError
import Scrapper.Controllo_tratte.Controller_tratte as Controller_tratte
import socket
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

amadeus = Client(
    client_id='mO1GSbwraiZUlQ84AJWQPE6GkxINddt1',
    client_secret='ungA0GVVriDUeztB'
)
# trattegestite = 1 #numero di tratte da cercare, potremmo inserirlo insieme al file dei parametri e me li faccio passare
# tratte = Controller_tratte.leggi_file()  caso get method, inserire controllo errore (nel caso controllo tratte � down le tratte devono restare quelle non aggiornate)
# trattegestite = len(tratte)
global incomes
def inviotratta(data):
    print(response)

@app.route('/recuperodati_scraper', methods=['POST']) 
def comunicazionepost():
    #incomes.append(request.get_json())
    incomes = request.form['tratte']
    return '', 204    
  
def controllo_tratta(user_id,OC,DC,DD,A):
    try:
        controllo = amadeus.shopping.flight_offers_search.get(originLocationCode=OC, destinationLocationCode=DC, departureDate=DD, adults=A) #se devo mandare un json con i parametri devo usare il post method
        data=f"{OC} {DC} {DD} {A}"
        #Controller_tratte.scrivi_file(data) su file
        #data=[user_id, OC, DC, DD, A]
        #COntroller_tratte.scrivi_database(data) su database
    except ResponseError as error:
         raise error
def richiesta_tratte():
    # Crea un socket TCP/IP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connette il socket alla porta dove il server è in ascolto
    server_address = ('localhost', 12345)
    sock.connect(server_address)

    try:
        # # Invia dati
        # message = 'Richiesta di un vettore'
        # sock.sendall(message.encode('utf-8'))

        # Aspetta la risposta
        data = sock.recv(1024)
        tratte = json.loads(data.decode('utf-8'))
        print('Vettore ricevuto {!r}'.format(tratte))

    finally:
        print('Chiusura del socket')
        sock.close()
        return tratte
    
while True:
    tratte=richiesta_tratte()
    trattegestite=len(tratte)
    #body = json.loads(json_string)   nel caso metodo get non ho bisogno del json per� posso farmi passare meno parametri dall'utente per� � pure un casino fare il json
    for i in range (1,trattegestite):
        try:
            response = amadeus.shopping.flight_offers_search.get(originLocationCode=tratte[0], destinationLocationCode=tratte[1], departureDate=tratte[2], adults=tratte[3])
            #response = amadeus.shopping.flight_offers_search.get(originLocationCode='SYD', destinationLocationCode='BKK', departureDate='2023-12-08', adults=1) se devo mandare un json con i parametri devo usare il post method
            # response = amadeus.shopping.flight_offers_search.post(body) nel caso post method
            # biaogna fare una response in cui tutti i paramentri variano al variare di i, quindi magare un microservizio che scrive e legge un file e mi invia un array di stringhe , 
            # print(response.data)
            inviotratta(response) #funzione che permette di inviare al topic kafka la tratta ottenuta
        except ResponseError as error:
            raise error
    
#Damiano qui si deve aggiungere anche la ricerca search_flight_inspiration o qualcosa
#del genere, te l'avevo inviato su telegram, per le offerte speciali in partenza
#da un aeroporto specifico
