
from kafka import KafkaConsumer
import sqlite3
import json
import requests
import threading


def invioNotifier(notifiche):
    print(notifiche)
    while True:
        response = requests.post('http://localhost:5003/recuperomail', json={'notifiche':notifiche})
        if response == 'ok':
            break

def leggi_topic_tratte():
    # Crea consumatore Kafka
    consumer_tratta = KafkaConsumer('Tratte',
                            bootstrap_servers=['localhost:29092'],
                            enable_auto_commit=False,
                            value_deserializer=lambda m: json.loads(m.decode('utf-8'))) #quest'ultimo valore da controllare
    notifiche = []
    for messages in consumer_tratta:
        # Ottieni il messaggio dal topic Kafka
        # msg = message.value
        for message in messages.value:
            result = requests.post('http://localhost:5000/trova_email_by_tratta', json={'ori':message.value['origin'], 'dest': message.value['destination'],'pr': message.value['price']})
        #result = UserController.trova_email_by_tratta(message.origin,message.destination,message.price)
            if result['email'] is not None:
                print(f"esiste almeno un user_id con quelle regole: {result}")  #bisogna inviare al notify lo user_id(o e-mail) e il msg
                notifiche.append(result['email'],message)
                # invioNotifier(result,msg)
            else:
                print("messaggio non destinato a un utente") # qui si potrebbe fare un meccanismo che elimina dal database la tratta, al proposito potrebbe aver senso cancellarla la tratta
    try:
        consumer_tratta.commit(messages.offset+1)
    except Exception as e:
        print("Commit failed due to : "+ e)
        e.printStackTrace()
    invioNotifier(notifiche)

def leggi_topic_aeroporti():
    # Crea consumatore Kafka
    consumer_aeroporto = KafkaConsumer('Aeroporti',
                            bootstrap_servers=['localhost:29092'],
                            enable_auto_commit=False,
                            value_deserializer=lambda m: json.loads(m.decode('utf-8'))) #quest'ultimo valore da controllare
    notifiche = []
    for messages in consumer_aeroporto:
        #msg = message.value
        for message in messages.value:
            result = requests.post('http://localhost:5000/trova_email_by_offerte', json={'ori':message.origin})
            if result['email'] is not None:
                print(f"esiste almeno un user_id con quelle regole: {result}")  #bisogna inviare al notify lo user_id(o e-mail) e il msg
                notifiche.append(result['email'],message)
                # invioNotifier(result,msg)
            else:
                print("messaggio non destinato a un utente") # qui si potrebbe fare un meccanismo che elimina dal database la tratta, al proposito potrebbe aver senso cancellarla la tratta
    try:
        consumer_aeroporto.commit(messages.offset+1)
    except Exception as e:
        print("Commit failed due to : "+ e)
        e.printStackTrace()
    invioNotifier(notifiche)


if __name__ == "__main__":
    # Creazione del primo thread
    t1 = threading.Thread(target=leggi_topic_tratte)

    # Creazione del secondo thread
    t2 = threading.Thread(target=leggi_topic_aeroporti)

    # Avvio dei thread
    t1.start()
    t2.start()


