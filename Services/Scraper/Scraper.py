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
import mysql.connector
import os

app = Flask(__name__)

amadeus = Client(
    client_id='VGSEQ2nHW7nHDGB1oBOMSsmXBYwWMEkQ',
    client_secret='qtXqxyhlSA4lMrO'+'d'
)
while(True):
    try:
        conn = mysql.connector.connect(user='root', password='password', host='mysql', database='scraper')
        cursor = conn.cursor()
        break
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
        time.sleep(10)

    
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

#TO_DO non so perchè chiedeva data quando doveva essere response, sarà cambiato con un conflitto di merge
def trova_prezzo_aeroporto(response):
    aeroporti_speciali=[]
    for offer in response.data:
        prezzo= round(float(offer["price"]["total"]) * 0.91,2)
        aeroporti_speciali.append({'origin':offer["origin"],'destination':offer["destination"], 'price':prezzo, "partenza": offer["departureDate"]})
    return aeroporti_speciali

def recupero_tratte():
    try:
        # Esegui una query SQL
        cursor.execute("SELECT * FROM tratte_salvate")

        # Ottieni i risultati
        risultati = cursor.fetchall()
    except mysql.connector.Error as e:
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
def recupero_aeroporti():
    try:
        # Esegui una query SQL
        cursor.execute("SELECT * FROM aeroporti_salvati")

        # Ottieni i risultati
        risultati = cursor.fetchall()
    except mysql.connector.Error as e:
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

#     response=requests.post('http://controllertratta-service:5002/invio_Scraper', json={'request':'tratta'})
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
#     response = requests.post('http://controllertratta-service:5002/invio_Scraper', json={'request':'aeroporto'})
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

@circuit(failure_threshold=5,recovery_timeout=43200)
def chiedi_tratte_controller_tratte():
    try:
        response=requests.post('http://controllertratta-service:5002/invio_Scraper', json={'request':'tratta'})
        if  response.text != 'error':
            data = response.json()
            print("ho ricevuto tratte da controller ",data)
            # return tratte
            cursor.execute("TRUNCATE TABLE tratte_salvate")
            query = "INSERT INTO tratte_salvate ( origine, destinazione, adulti) VALUES (%s, %s, %s)" #aggiunti adulti
            for item in data:
                cursor.execute(query, (item['origine'], item['destinazione'], item['adulti']))
                conn.commit()
            # cursor.execute(query, (data['origine'], data['destinazione'], data['adulti']))
            # conn.commit()
    except Exception as e:
        print(f"Errore durante la richiesta delle tratte: {e}")
        raise e #TO_DO o il print o il raise, in realtà non andrebbe terminato il programma,andrebbe controllato se obbligato dal circuit breaker

        
@circuit(failure_threshold=5,recovery_timeout=43200)
def chiedi_aeroporti_controller_tratte():
    try:
        response = requests.post('http://controllertratta-service:5002/invio_Scraper', json={'request':'aeroporto'})
        if response.text != 'error':
            data = response.json()
            print("ho ricevuto aeroporti da controller ",data)
            # return aeroporti
            cursor.execute("TRUNCATE TABLE aeroporti_salvati")
            query = "INSERT INTO aeroporti_salvati ( origine) VALUES (%s )" #TO_DO da modificare se vogliamo aggiungere adults
            # cursor.execute(query, (data['aeroporto'],))
            for item in data:
                cursor.execute(query, (item['aeroporto']),)
                conn.commit()
            # conn.commit()
    except Exception as e:
        print(f"Errore durante la richiesta delgli aeroporti: {e}")
        raise e #TO_DO o il print o il raise, in realtà non andrebbe terminato il programma,andrebbe controllato se obbligato dal circuit breaker


# #aggiungere un altro database
# aeroporti = {}
# tratte = {}
# while True:
#     #tratte,aeroporti=richiesta_tratte()
#     domani = datetime.now() + timedelta(days=1) 
#     data_domani = domani.strftime('%Y-%m-%d')

#     #mettere le url come variabili d'ambiente
#     response=requests.post('http://controllertratta-service:5002/invio_Scraper', json={'request':'tratta'})
#     if  response.text != 'error':
#         tratte = response.json()
#         print("ho ricevuto tratte da controller")
#     for tratta in tratte:
#         try:
#             # print("data ",data_domani, tratta["origine"], tratta["destinazione"])
#             response = amadeus.shopping.flight_offers_search.get(originLocationCode=tratta["origine"], destinationLocationCode=tratta["destinazione"], departureDate=data_domani, adults=tratta["adulti"], max=5) 
#             data = trova_prezzo_tratta(response,tratta["origine"],tratta["destinazione"],tratta["adulti"]) #TO_DO non so se devi aggiungere adulti qui
#             inviotratta(data) #funzione che permette di inviare al topic kafka la tratta ottenuta
#             time.sleep(0.5)
#         except ResponseError as error:
#             print(f"Errore durante l'esecuzione della chiamata API: {error}")
    
#     response = requests.post('http://controllertratta-service:5002/invio_Scraper', json={'request':'aeroporto'})
#     if response.text != 'error':
#         aeroporti = response.json()
#         print("ho ricevuto aeroporti da controller")
#     for aeroporto in aeroporti:
#         try:
#             response = amadeus.shopping.flight_destinations.get(origin=aeroporto["origine"],departureDate=data_domani,oneWay=True,nonStop=True)  
#             data = trova_prezzo_aeroporto(response)
#             invioaeroporto(data) #funzione che permette di inviare al topic kafka la tratta ottenuta
#             time.sleep(0.1)
#         except ResponseError as error:
#             print(f"Errore durante l'esecuzione della chiamata API: {error}")
#     time.sleep(86400)

    

while True:
    domani = datetime.now() + timedelta(days=1) 
    data_domani = domani.strftime('%Y-%m-%d')
    try:
        chiedi_tratte_controller_tratte()
        tratte=recupero_tratte()
    except Exception as e:
        print(f"errore durante la richiesta: {e}")
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
        chiedi_aeroporti_controller_tratte()
        aeroporti=recupero_aeroporti()
    except Exception as e:
        print(f"errore durante la richiesta: {e}")  
    for aeroporto in aeroporti:
        try:
            response = amadeus.shopping.flight_destinations.get(origin=aeroporto["origine"],departureDate=data_domani,oneWay=True,nonStop=True)  
            data = trova_prezzo_aeroporto(response)
            invioaeroporto(data) #funzione che permette di inviare al topic kafka la tratta ottenuta
            time.sleep(0.5)
        except ResponseError as error:
            print(f"Errore durante l'esecuzione della chiamata API: {error}")
    time.sleep(86400)
