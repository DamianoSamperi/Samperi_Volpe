
from amadeus import Client, ResponseError
from kafka import KafkaProducer,errors
import kafka
import json
from flask import Flask, request
import time
import requests
import threading
from datetime import datetime, timedelta
from circuitbreaker import circuit,CircuitBreakerError
import mysql.connector
import os
import prometheus_client

app = Flask(__name__)
scraping_time = prometheus_client.Gauge('scraping_time', 'tempo di scraping')
scraping_time.set(0)
prometheus_client.start_http_server(9999)

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
        producer = KafkaProducer(bootstrap_servers=['kafka-service:9092'],value_serializer=lambda v: json.dumps(v).encode('utf-8')) 
        print("connesso al broker")
        break
    except errors.NoBrokersAvailable as error:
        print("kafka non disponibile")
        time.sleep(15)


def inviotratta(data):
    if data != []:
        producer.send('Tratte', data)
        #flush dovrebbe aspettare che il messaggio venga effettivamente inviato
        print("sto inviando a kafka: ",data)
        producer.flush()
def invioaeroporto(data):
    if data != []:
        producer.send('Aeroporti', data)
        producer.flush()

def trova_prezzo_tratta(response,origin,destination,adulti):
    tratte_speciali=[]   
    for offer in response.data:
            prezzo= round(float(offer["price"]["total"]) * 0.91,2)
            tratte_speciali.append({'origin':origin,'destination':destination, 'price': prezzo, 'adulti': adulti, "partenza": offer["itineraries"][0]["segments"][0]["departure"]["at"]})
    return tratte_speciali

def trova_prezzo_aeroporto(response):
    aeroporti_speciali=[]
    for offer in response.data:
        prezzo= round(float(offer["price"]["total"]) * 0.91,2)
        aeroporti_speciali.append({'origin':offer["origin"],'destination':offer["destination"], 'price':prezzo, "partenza": offer["departureDate"]})
    return aeroporti_speciali

def recupero_tratte():
    try:
        cursor.execute("SELECT * FROM tratte_salvate")

        risultati = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
        return "error"

    tratte = []
    
    for tupla in risultati:
        tratte.append({"origine": tupla[1] , "destinazione" : tupla[2], "adulti": tupla[3]}) #TO_DO Damiano credo sia giusto ma vedi tu

    return tratte

def recupero_aeroporti():
    try:
        cursor.execute("SELECT * FROM aeroporti_salvati")

        risultati = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
        return "error"

    aeroporti = []

    for tupla in risultati:
        aeroporti.append({"origine": tupla[1] })

    return aeroporti


@circuit(failure_threshold=5,recovery_timeout=43200)
def chiedi_tratte_controller_tratte():
    try:
        response=requests.post('http://controllertratta-service:5002/invio_Scraper', json={'request':'tratta'})
        if  response.text != 'error':
            data = response.json()
            print("ho ricevuto tratte da controller ",data)
            cursor.execute("TRUNCATE TABLE tratte_salvate")
            query = "INSERT INTO tratte_salvate ( origine, destinazione, adulti) VALUES (%s, %s, %s)"
            for item in data:
                cursor.execute(query, (item['origine'], item['destinazione'], item['adulti']))
                conn.commit()
            return True 
        
    except Exception as e:
        print(f"Errore durante la richiesta delle tratte: {e}")
        raise e

        
@circuit(failure_threshold=5,recovery_timeout=43200)
def chiedi_aeroporti_controller_tratte():
    try:
        response = requests.post('http://controllertratta-service:5002/invio_Scraper', json={'request':'aeroporto'})
        if response.text != 'error':
            data = response.json()
            print("ho ricevuto aeroporti da controller ",data)
            cursor.execute("TRUNCATE TABLE aeroporti_salvati")
            query = "INSERT INTO aeroporti_salvati ( origine) VALUES (%s )" 
            for item in data:
                cursor.execute(query, (item['origine'],))
                conn.commit()
            return True 
    except Exception as e:
        print(f"Errore durante la richiesta delgli aeroporti: {e}")
        raise e


aeroporti=[]
tratte=[]
while True:
    start_time=time.time()
    domani = datetime.now() + timedelta(days=1) 
    data_domani = domani.strftime('%Y-%m-%d')
    try:
        stato=False
        while not stato:
            try:
              stato=chiedi_tratte_controller_tratte()
            except requests.exceptions.ConnectionError:
              print("Connessione rifiutata riprovo a connettermi...\n")
            print("prova ciclo")
    except CircuitBreakerError:
        print("Microservizio momentaneamente down, faccio richiesta al database\n")
    finally:
        tratte=recupero_tratte()
        for tratta in tratte:
            try:
                print("data ",data_domani, tratta["origine"], tratta["destinazione"])
                response = amadeus.shopping.flight_offers_search.get(originLocationCode=tratta["origine"], destinationLocationCode=tratta["destinazione"], departureDate=data_domani, adults=tratta["adulti"], max=5) 
                data = trova_prezzo_tratta(response,tratta["origine"],tratta["destinazione"],tratta["adulti"]) #TO_DO non so se devi aggiungere adulti qui
                inviotratta(data) #funzione che permette di inviare al topic kafka la tratta ottenuta
                time.sleep(0.5)
            except ResponseError as error:
                print(f"Errore durante l'esecuzione della chiamata API: {error.code}")

        try:
            stato=False
            while not stato:
                try:
                    stato=chiedi_aeroporti_controller_tratte()
                except requests.exceptions.ConnectionError:
                    print("Connessione rifiutata riprovo a connettermi...\n")
                print("prova ciclo")
        except CircuitBreakerError:
            print("Microservizio momentaneamente down, faccio richiesta al database\n")
        finally:
            aeroporti=recupero_aeroporti()
            for aeroporto in aeroporti:
                try:
                    response = amadeus.shopping.flight_destinations.get(origin=aeroporto["origine"],departureDate=data_domani,oneWay=True,nonStop=True)  
                    data = trova_prezzo_aeroporto(response)
                    invioaeroporto(data) #funzione che permette di inviare al topic kafka la tratta ottenuta
                    time.sleep(0.5)
                except ResponseError as error:
                    print(f"Errore durante l'esecuzione della chiamata API: {error.code}") 
            end_time=time.time()
            tempo_scraping=end_time-start_time
            #setto la metrica per prometheus
            scraping_time.set(tempo_scraping) 
            time.sleep(86400)

