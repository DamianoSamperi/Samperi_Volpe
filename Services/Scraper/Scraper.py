# from msilib import Control
from amadeus import Client, ResponseError
from kafka import KafkaProducer,errors
import kafka
import json
from flask import Flask, request
import time
import requests
import threading
from datetime import datetime, timedelta
from circuitbreaker import circuit

app = Flask(__name__)

amadeus = Client(
    client_id='VGSEQ2nHW7nHDGB1oBOMSsmXBYwWMEkQ',
    client_secret='qtXqxyhlSA4lMrO'+'d'
)
while True:
    try:
        producer = KafkaProducer(bootstrap_servers=['kafka:9092'],value_serializer=lambda v: json.dumps(v).encode('utf-8')) 
        print("connesso al broker")
        break
    except errors.NoBrokersAvailable as error:
        print("kafka non disponibile")
        time.sleep(15)


def inviotratta(data):
    if data != []:
        producer.send('Tratte', data)
        #flush dovrebbe aspettare che il messaggio venga effettivamente inviato
        producer.flush()
def invioaeroporto(data):
    if data != []:
        producer.send('Aeroporti', data)
        producer.flush()

def trova_prezzo_tratta(response,origin,destination,adulti):
    tratte_speciali=[]   
    for offer in response.data:
            prezzo= round(float(offer["price"]["total"]) * 0.91,2)
            tratte_speciali.append({'origin':origin,'destination':destination, 'price': prezzo, 'adulti': adulti, "partenza": offer["itineraries"][0]["segments"][0]["departure"]["at"]}) #aggiunti adulti
    # prezzo= response.data[00]["price"]["total"] * 0.91
    return tratte_speciali

def trova_prezzo_aeroporto(data):
    aeroporti_speciali=[]
    for offer in response.data:
        prezzo= round(float(offer["price"]["total"]) * 0.91,2)
        aeroporti_speciali.append({'origin':offer["origin"],'destination':offer["destination"], 'price':prezzo, "partenza": offer["departureDate"]})
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

#     response=requests.post('http://controller_tratta:5002/invio_Scraper', json={'request':'tratta'})
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
#     response = requests.post('http://controller_tratta:5002/invio_Scraper', json={'request':'aeroporto'})
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


#prova circuit breaker, dovremmo fare in modo che se la funzione crasha troppe volte
#(di default è 5), allora fa le richieste ad amadeus con le tratte/aeroporti del
#giorno precedente, le funzioni devono lanciare un eccezione nel caso in cui
#la richiesta non vada a buon fine
'''
@circuit(failure_treshold=5,reset_timeout=43200)
def chiedi_tratte_controller_tratte():
    try:
        domani = datetime.now() + timedelta(days=1) 
        data_domani = domani.strftime('%Y-%m-%d')

        response=requests.post('http://controller_tratta:5002/invio_Scraper', json={'request':'tratta'})
        if  response.text != 'error':
            tratte = response.json()
            print("ho ricevuto tratte da controller")
            return tratte
    except Exception as e:
        print(f"Errore durante la richiesta delle tratte: {e}")
        raise
'''
'''
 @circuit(failure_treshold=5,reset_timeout=43200)
 def chiedi_aeroporti_controller_tratte():
    try:
        domani = datetime.now() + timedelta(days=1) 
        data_domani = domani.strftime('%Y-%m-%d')

        response = requests.post('http://controller_tratta:5002/invio_Scraper', json={'request':'aeroporto'})
        if response.text != 'error':
            aeroporti = response.json()
            print("ho ricevuto aeroporti da controller")
            return aeroporti
    except Exception as e:
        print(f"Errore durante la richiesta delgli aeroporti: {e}")
        raise
'''         

aeroporti = {}
tratte = {}
while True:
    #tratte,aeroporti=richiesta_tratte()
    domani = datetime.now() + timedelta(days=1) 
    data_domani = domani.strftime('%Y-%m-%d')

    response=requests.post('http://controller_tratta:5002/invio_Scraper', json={'request':'tratta'})
    if  response.text != 'error':
        tratte = response.json()
        print("ho ricevuto tratte da controller")
    for tratta in tratte:
        try:
            # print("data ",data_domani, tratta["origine"], tratta["destinazione"])
            response = amadeus.shopping.flight_offers_search.get(originLocationCode=tratta["origine"], destinationLocationCode=tratta["destinazione"], departureDate=data_domani, adults=tratta["adulti"], max=5) 
            data = trova_prezzo_tratta(response,tratta["origine"],tratta["destinazione"],tratta["adulti"]) #TO_DO non so se devi aggiungere adulti qui
            inviotratta(data) #funzione che permette di inviare al topic kafka la tratta ottenuta
            time.sleep(0.5)
        except ResponseError as error:
            print(f"Errore durante l'esecuzione della chiamata API: {error}")
    
    response = requests.post('http://controller_tratta:5002/invio_Scraper', json={'request':'aeroporto'})
    if response.text != 'error':
        aeroporti = response.json()
        print("ho ricevuto aeroporti da controller")
    for aeroporto in aeroporti:
        try:
            response = amadeus.shopping.flight_destinations.get(origin=aeroporto["origine"],departureDate=data_domani,oneWay=True,nonStop=True)  
            data = trova_prezzo_aeroporto(response)
            invioaeroporto(data) #funzione che permette di inviare al topic kafka la tratta ottenuta
            time.sleep(0.1)
        except ResponseError as error:
            print(f"Errore durante l'esecuzione della chiamata API: {error}")
    time.sleep(86400)

    
'''
while True:
    try:
        tratte=chiedi_tratte_controller_tratte()
    except Exception as e:
        print("errore durante la richiesta: {e}")
    for tratta in tratte:
        try:
            # print("data ",data_domani, tratta["origine"], tratta["destinazione"])
            response = amadeus.shopping.flight_offers_search.get(originLocationCode=tratta["origine"], destinationLocationCode=tratta["destinazione"], departureDate=data_domani, adults=tratta["adulti"], max=5) 
            data = trova_prezzo_tratta(response,tratta["origine"],tratta["destinazione"],tratta["adulti"]) #TO_DO non so se devi aggiungere adulti qui
            inviotratta(data) #funzione che permette di inviare al topic kafka la tratta ottenuta
            time.sleep(0.5)
        except ResponseError as error:
            print(f"Errore durante l'esecuzione della chiamata API: {error}")

    try:
        aeroporti=chiedi_aeroporti_controller_tratte()
    except Exception as e:
        print("errore durante la richiesta: {e}")  
    for aeroporto in aeroporti:
        try:
            response = amadeus.shopping.flight_destinations.get(origin=aeroporto["origine"],departureDate=data_domani,oneWay=True,nonStop=True)  
            data = trova_prezzo_aeroporto(response)
            invioaeroporto(data) #funzione che permette di inviare al topic kafka la tratta ottenuta
            time.sleep(0.1)
        except ResponseError as error:
            print(f"Errore durante l'esecuzione della chiamata API: {error}")
    time.sleep(86400)
'''