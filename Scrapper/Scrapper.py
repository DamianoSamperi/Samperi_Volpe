from msilib import Control
from amadeus import Client, ResponseError
import socket
from kafka import KafkaProducer
import json
from flask import Flask, jsonify, request
import time
import requests
import threading
from datetime import datetime, timedelta

app = Flask(__name__)

amadeus = Client(
    client_id='mO1GSbwraiZUlQ84AJWQPE6GkxINddt1',
    client_secret='ungA0GVVriDUeztB'
)
#TO-DO vanno controllati i parametri di configurazione kafka
producer = KafkaProducer(bootstrap_servers='localhost:29092',value_serializer=lambda v: json.dumps(v).encode('utf-8')) #TO_DO ultimo valore da controllare, dovrebbe servire a inviare json

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
    for offer in response.data:
            prezzo= offer["price"]["total"] * 0.91
            tratte_speciali.append({'origin':origin,'destination':destination, 'price': prezzo})
    # prezzo= response.data[00]["price"]["total"] * 0.91
    return tratte_speciali

def trova_prezzo_aeroporto(data):
    aeroporti_speciali=[]
    for offer in response.data:
        prezzo= offer["price"]["total"] * 0.91
        aeroporti_speciali.append({'origin':offer["origin"],'destination':offer["destination"], 'price':prezzo})
    return aeroporti_speciali

#TO_DO Possibilità utilizzo thread
# lock = threading.Lock()
# def richiesta_api(richiesta,data,data_domani):
#     # Acquisisci il lock
#     with lock:
#         if richiesta=='tratta':
#             return amadeus.shopping.flight_offers_search.get(originLocationCode=data[1], destinationLocationCode=data[2], departureDate= data_domani, adults=data[3])
#         elif richiesta== 'aroporto':
#             return amadeus.shopping.flight_destinations.get(origin=data[0],oneWay=True,nonStop=True)  
#         time.sleep(0.1)

# def Richiesta_API_Tratta():
#     domani = datetime.now() + timedelta(days=1) 
#     data_domani = domani.strftime('%Y-%m-%d')

#     response=requests.post('http://localhost:5002/invio_Scraper', json={'request':'tratta'})
#     if  response != 'error':
#       tratte = response
#     for tratta in tratte:
#         try:
#             response = richiesta_api('tratta',tratta,data_domani) 
#             data = trova_prezzo_tratta(response,tratte[0],tratte[1])
#             inviotratta(data) #funzione che permette di inviare al topic kafka la tratta ottenuta
#         except ResponseError as error:
#             raise error
#         time.sleep(86400)

# def Richiesta_API_Aeroporto():
#     domani = datetime.now() + timedelta(days=1) 
#     data_domani = domani.strftime('%Y-%m-%d')
#     response = requests.post('http://localhost:5002/invio_Scraper', json={'request':'aeroporto'})
#     if response != 'error':
#         aeroporti = response
#     for aeroporto in aeroporti:
#         try:
#             response = richiesta_api('aeroporto',aeroporto,data_domani)   
#             data = trova_prezzo_aeroporto(response)
#             invioaeroporto(response) #funzione che permette di inviare al topic kafka la tratta ottenuta
#         except ResponseError as error:
#             raise error
#         time.sleep(86400)

# # Creazione del primo thread
# t1 = threading.Thread(target=Richiesta_API_Tratta)

# # Creazione del secondo thread
# t2 = threading.Thread(target=Richiesta_API_Aeroporto)

# # Avvio dei thread
# t1.start()
# t2.start()


            

aeroporti = {}
tratte = {}
while True:
    #tratte,aeroporti=richiesta_tratte()
    domani = datetime.now() + timedelta(days=1) 
    data_domani = domani.strftime('%Y-%m-%d')

    response=requests.post('http://localhost:5002/invio_Scraper', json={'request':'tratta'})
    if  response.text != 'error':
        tratte = response.json()
    for tratta in tratte:
        try:
            # print("data ",data_domani, tratta["origine"], tratta["destinazione"])
            response = amadeus.shopping.flight_offers_search.get(originLocationCode=tratta["origine"], destinationLocationCode=tratta["destinazione"], departureDate=data_domani, adults=1) 
            data = trova_prezzo_tratta(response,tratta["origine"],tratta["destinazione"])
            inviotratta(data) #funzione che permette di inviare al topic kafka la tratta ottenuta
            time.sleep(0.1)
        except ResponseError as error:
            print(f"Errore durante l'esecuzione della chiamata API: {error}")
         
    response = requests.post('http://localhost:5002/invio_Scraper', json={'request':'aeroporto'})
    if response.text != 'error':
        aeroporti = response.json()
    for aeroporto in aeroporti:
        try:
            response = amadeus.shopping.flight_destinations.get(origin=aeroporto["origine"],oneWay=True,nonStop=True)  
            data = trova_prezzo_aeroporto(response)
            invioaeroporto(response) #funzione che permette di inviare al topic kafka la tratta ottenuta
            time.sleep(0.1)
        except ResponseError as error:
            print(f"Errore durante l'esecuzione della chiamata API: {error}")
    time.sleep(86400)

    