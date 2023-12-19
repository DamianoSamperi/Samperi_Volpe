from msilib import Control
from amadeus import Client, ResponseError
import Samperi_Volpe.Scrapper.Controller_tratte as Controller_tratte
import socket
from kafka import KafkaProducer
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

amadeus = Client(
    client_id='mO1GSbwraiZUlQ84AJWQPE6GkxINddt1',
    client_secret='ungA0GVVriDUeztB'
)
#TO-DO vanno controllati i parametri di configurazione kafka
producer = KafkaProducer(bootstrap_servers='localhost:9092',value_serializer=lambda v: json.dumps(v).encode('utf-8')) #TO_DO ultimo valore da controllare, dovrebbe servire a inviare json

global incomes

def inviotratta(data):
    producer.send('Tratte', data)
    # TO_DO controlla se necessario
    producer.flush()
def invioaeroporto(data):
    producer.send('Aeroporti', data)
    # TO_DO controlla se necessario
    producer.flush()

@app.route('/recuperodati_scraper', methods=['POST']) 
def comunicazionepost():
    #incomes.append(request.get_json())
    incomes = request.form['vet_tratte']
    # return '', 204    
  
#TO_DO probabilmente va cambiata da comunicazione con socket a quella con flask
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
def trova_prezzo_tratta(response,origin,destination):
    tratte_speciali=[]
    prezzo= response.data[00]["price"]["total"] * 0.91
    tratte_speciali.append({'origin':origin,'destination':destination, 'price': prezzo})
    return tratte_speciali

def trova_prezzo_aeroporto(data):
    tratte_speciali=[]
    for i in 5:
        if data.data[i] is not None:
            prezzo= data.data[i]["price"]["total"] * 0.91
            tratte_speciali.append({'origin':'data.data[i]["origin"]','destination':'data.data[i]["destination"]', 'price':prezzo})
    return tratte_speciali

while True:
    tratte,aeroporti=richiesta_tratte()
    trattegestite=len(tratte)
    aeroportigestiti=len(aeroporti)
    for i in range (1,trattegestite):
        try:
            #TO_DO bisogna variare con i quindi bisogna controllare cosa ritorna effettivamente richiesta_tratte
            response = amadeus.shopping.flight_offers_search.get(originLocationCode=tratte[0], destinationLocationCode=tratte[1], departureDate=tratte[2], adults=tratte[3]) 
            #TO_DO un realtà la data non viene salvata ma va aggiunta quella del giorno dopo
            data = trova_prezzo_tratta(response,tratte[0],tratte[1])
            inviotratta(data) #funzione che permette di inviare al topic kafka la tratta ottenuta
        except ResponseError as error:
            raise error
    for i in range (1,aeroportigestiti):
        try:
            #TO_DO bisogna variare con i quindi bisogna controllare cosa ritorna effettivamente richiesta_tratte
            response = amadeus.shopping.flight_destinations.get(origin=aeroporti[i])  
            data = trova_prezzo_aeroporto(response)
            invioaeroporto(response) #funzione che permette di inviare al topic kafka la tratta ottenuta
        except ResponseError as error:
            raise error
    
