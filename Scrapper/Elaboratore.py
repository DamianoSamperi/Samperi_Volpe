
from kafka import KafkaConsumer
import sqlite3
import json
import UserController
import requests


# Crea un consumatore Kafka
consumer_tratta = KafkaConsumer('tratte',
                         bootstrap_servers=['localhost:9092'],
                         value_deserializer=lambda m: json.loads(m.decode('utf-8'))) #quest'ultimo valore da controllare

consumer_aeroporto = KafkaConsumer('aeroporti',
                         bootstrap_servers=['localhost:9092'],
                         value_deserializer=lambda m: json.loads(m.decode('utf-8'))) #quest'ultimo valore da controllare

def invioNotifier(notifiche):
    print(notifiche)
    response = requests.post('http://localhost:5000/recuperomail', {'notifiche':'notifiche'})
    # return response.text   
#TO_DO comunicazione con Notifier

notifiche = []
for message in consumer_tratta:
    # Ottieni il messaggio dal topic Kafka
    msg = message.value
    
    result = UserController.trova_email_by_tratta(msg)
    if result is not None:
        print(f"esiste almeno un user_id con quelle regole: {result}")  #bisogna inviare al notify lo user_id(o e-mail) e il msg
        notifiche.append(result,msg)
        # invioNotifier(result,msg)
    else:
        print("messaggio non destinato a un utente") # qui si potrebbe fare un meccanismo che elimina dal database la tratta, al proposito potrebbe aver senso cancellarla la tratta
for message in consumer_aeroporto:
    msg = message.value
    
    result = UserController.trova_email_by_offerte(msg)
    if result is not None:
        print(f"esiste almeno un user_id con quelle regole: {result}")  #bisogna inviare al notify lo user_id(o e-mail) e il msg
        notifiche.append(result,msg)
        # invioNotifier(result,msg)
    else:
        print("messaggio non destinato a un utente") # qui si potrebbe fare un meccanismo che elimina dal database la tratta, al proposito potrebbe aver senso cancellarla la tratta
invioNotifier(notifiche) 