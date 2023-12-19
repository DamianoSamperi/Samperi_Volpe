
from kafka import KafkaConsumer
import sqlite3
import json
import UserController
import requests


# Crea un consumatore Kafka
consumer = KafkaConsumer('tratte',
                         bootstrap_servers=['localhost:9092'],
                         value_deserializer=lambda m: json.loads(m.decode('utf-8'))) #quest'ultimo valore da controllare

def invioNotifier(notifiche):
    print(notifiche)
    response = requests.post('http://localhost:5000/recuperomail', {'notifiche':'notifiche'})
    # return response.text   

# def invioNotifier(data,msg):
#     print(data)
#     response = requests.post('http://localhost:5000/recuperomail', data=data,msg=msg)
#     return response.text   
    #TO_DO comunicazione con Notifier

for message in consumer:
    # Ottieni il messaggio dal topic Kafka
    notifiche = []
    msg = message.value
    
    result = UserController.trova_email(msg)
    if(UserController.torna_budget(result)<):
        if result is not None:
            print(f"esiste almeno un user_id con quelle regole: {result}")  #bisogna inviare al notify lo user_id(o e-mail) e il msg
            notifiche.append(result,msg)
            # invioNotifier(result,msg)
        else:
            print("messaggio non destinato a un utente") # qui si potrebbe fare un meccanismo che elimina dal database la tratta, al proposito potrebbe aver senso cancellarla la tratta
        invioNotifier(notifiche) 