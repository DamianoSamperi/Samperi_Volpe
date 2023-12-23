from msilib import Control
from amadeus import Client, ResponseError
import socket
from kafka import KafkaProducer
import json
from flask import Flask, jsonify, request
import time
import requests

app = Flask(__name__)

amadeus = Client(
    client_id='mO1GSbwraiZUlQ84AJWQPE6GkxINddt1',
    client_secret='ungA0GVVriDUeztB'
)
#TO-DO vanno controllati i parametri di configurazione kafka
producer = KafkaProducer(bootstrap_servers='localhost:9092',value_serializer=lambda v: json.dumps(v).encode('utf-8')) #TO_DO ultimo valore da controllare, dovrebbe servire a inviare json

# global incomes


def inviotratta(data):
    producer.send('Tratte', data)
    #flush dovrebbe aspettare che il messaggio venga effettivamente inviato
    producer.flush()
def invioaeroporto(data):
    producer.send('Aeroporti', data)
    producer.flush()

#TO_DO questi nel caso vogliamo aggiornare ad ogni inserimento su daatabase di controller_tratte
# @app.route('/recupero_tratte_scraper', methods=['POST']) 
# def comunicazionepost():
#     #incomes.append(request.get_json())
#     global tratte 
#     tratte = request.form['vet_tratte']

# @app.route('/recupero_aeroporti_scraper', methods=['POST']) 
# def comunicazionepost():
#     #incomes.append(request.get_json())
#     global aeroporti 
#     aeroporti = request.form['vet_aeroporti']


def trova_prezzo_tratta(response,origin,destination):
    tratte_speciali=[]
    prezzo= response.data[00]["price"]["total"] * 0.91
    tratte_speciali.append({'origin':origin,'destination':destination, 'price': prezzo})
    return tratte_speciali

def trova_prezzo_aeroporto(data):
    aeroporti_speciali=[]
    for i in 5:
        if data.data[i] is not None:
            prezzo= data.data[i]["price"]["total"] * 0.91
            aeroporti_speciali.append({'origin':'data.data[i]["origin"]','destination':'data.data[i]["destination"]', 'price':prezzo})
    return aeroporti_speciali

while True:
    #tratte,aeroporti=richiesta_tratte()
    response=requests.post('http://localhost:5000/invio_Scraper', {'request':'tratta'})
    if  response != 'error':
        tratte = response
    trattegestite=len(tratte)
    for i in range (1,trattegestite):
        try:
            #TO_DO bisogna variare con i quindi bisogna controllare cosa ritorna effettivamente richiesta_tratte
            response = amadeus.shopping.flight_offers_search.get(originLocationCode=tratte[0], destinationLocationCode=tratte[1], departureDate=tratte[2], adults=tratte[3]) 
            #TO_DO un realtà la data non viene salvata ma va aggiunta quella del giorno dopo
            data = trova_prezzo_tratta(response,tratte[0],tratte[1])
            inviotratta(data) #funzione che permette di inviare al topic kafka la tratta ottenuta
        except ResponseError as error:
            raise error
         
    response = requests.post('http://localhost:5000/invio_Scraper', {'request':'aeroporto'})
    if response != 'error':
        aeroporti = response
    aeroportigestiti=len(aeroporti)
    for i in range (1,aeroportigestiti):
        try:
            #TO_DO bisogna variare con i quindi bisogna controllare cosa ritorna effettivamente richiesta_tratte
            response = amadeus.shopping.flight_destinations.get(origin=aeroporti[i],oneWay=True,nonStop=True)  
            data = trova_prezzo_aeroporto(response)
            invioaeroporto(response) #funzione che permette di inviare al topic kafka la tratta ottenuta
        except ResponseError as error:
            raise error
    time.sleep(86400)

    
