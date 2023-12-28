
from kafka import KafkaConsumer
import sqlite3
import json
import requests


# Crea consumatore Kafka
consumer_tratta = KafkaConsumer('tratte',
                        bootstrap_servers=['localhost:9092'],
                        enable_auto_commit=False,
                        value_deserializer=lambda m: json.loads(m.decode('utf-8'))) #quest'ultimo valore da controllare

consumer_aeroporto = KafkaConsumer('aeroporti',
                        bootstrap_servers=['localhost:9092'],
                        enable_auto_commit=False,
                        value_deserializer=lambda m: json.loads(m.decode('utf-8'))) #quest'ultimo valore da controllare

def invioNotifier(notifiche):
    print(notifiche)
    while True:
        response = requests.post('http://localhost:5000/recuperomail', json={'notifiche':notifiche})
        if response == 'ok':
            break

notifiche = []
for message in consumer_tratta:
    # Ottieni il messaggio dal topic Kafka
    # msg = message.value

    result = requests.post('http://localhost:5000/trova_email_by_tratta', json={'ori':message.value['origin'], 'dest': message.value['destination'],'pr': message.value['price']})
   #result = UserController.trova_email_by_tratta(message.origin,message.destination,message.price)
    if result['email'] is not None:
        print(f"esiste almeno un user_id con quelle regole: {result}")  #bisogna inviare al notify lo user_id(o e-mail) e il msg
        notifiche.append(result['email'],message)
        # invioNotifier(result,msg)
    else:
        print("messaggio non destinato a un utente") # qui si potrebbe fare un meccanismo che elimina dal database la tratta, al proposito potrebbe aver senso cancellarla la tratta
try:
    consumer_tratta.commit(message.offset+1)
except Exception as e:
    print("Commit failed due to : "+ e)
    e.printStackTrace()

for message in consumer_aeroporto:
    #msg = message.value
    result = requests.post('http://localhost:5000/trova_email_by_offerte', json={'ori':message.origin})
    result.json
    if result['email'] is not None:
        print(f"esiste almeno un user_id con quelle regole: {result}")  #bisogna inviare al notify lo user_id(o e-mail) e il msg
        notifiche.append(result['email'],message)
        # invioNotifier(result,msg)
    else:
        print("messaggio non destinato a un utente") # qui si potrebbe fare un meccanismo che elimina dal database la tratta, al proposito potrebbe aver senso cancellarla la tratta
try:
    consumer_aeroporto.commit(message.offset+1)
except Exception as e:
    print("Commit failed due to : "+ e)
    e.printStackTrace()

invioNotifier(notifiche) 