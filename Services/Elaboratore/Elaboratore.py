from kafka import KafkaConsumer
import time
import json
import requests
import threading


def invioNotifier(notifiche):
    print(notifiche)
    while True:
        response = requests.post('http://notifier:5003/recuperomail', json={'notifiche':notifiche})
        if response == 'ok':
            break

def leggi_topic_tratte():
    # Crea consumatore Kafka
    while True:
        try:
            consumer_tratta = KafkaConsumer('Tratte',
                                    bootstrap_servers=['kafka:9092'],
                                    group_id='grp1',
                                    enable_auto_commit=False,
                                    value_deserializer=lambda m: json.loads(m.decode('utf-8'))) #quest'ultimo valore da controllare
            break
        except Exception as error:
            print("kafka non disponibile")
            time.sleep(15)
   
    notifiche = []
    for messages in consumer_tratta:
        # Ottieni il messaggio dal topic Kafka
        # msg = message.value
        for message in messages.value:
            result = requests.post('http://user_controller:5000/trova_email_by_tratta', json={'ori':message['origin'], 'dest': message['destination'],'pr': message['price'] })
        #result = UserController.trova_email_by_tratta(message.origin,message.destination,message.price)
            print("result ",result.json())
            emails=result.json()
            if emails is not None:
                print(f"esiste almeno un user_id con quelle regole: {emails}")  #bisogna inviare al notify lo user_id(o e-mail) e il msg
                for email in emails:
                    print("emails ",emails)
                    print("email ",email)
                    notifiche.append({"email": email[0],"message":message})
                # invioNotifier(result,msg)
            else:
                print("messaggio non destinato a un utente") # qui si potrebbe fare un meccanismo che elimina dal database la tratta, al proposito potrebbe aver senso cancellarla la tratta
        try:
            offset=messages.offset
            offsets = {'Tratte': offset + 1}          
            consumer_tratta.commit(offsets)
        except Exception as e:
            print("Commit failed due to : ", e)
        invioNotifier(notifiche)

def leggi_topic_aeroporti():
    # Crea consumatore Kafka
    while True:
        try:            
            consumer_aeroporto = KafkaConsumer('Aeroporti',
                                    bootstrap_servers=['kafka:9092'],
                                    group_id='grp1',
                                    enable_auto_commit=False,
                                    value_deserializer=lambda m: json.loads(m.decode('utf-8'))) #quest'ultimo valore da controllare
            break
        except Exception as error :
            print("kafka non disponibile")
            time.sleep(15)
    notifiche = []
    for messages in consumer_aeroporto:
        #msg = message.value
        for message in messages.value:
            result = requests.post('http://user_controller:5000/trova_email_by_offerte', json={'ori':message['origin'], 'dest': message['destination'],'pr': message['price']})
            emails=result.json()
            if emails is not None:
                print(f"esiste almeno un user_id con quelle regole: {emails}")  #bisogna inviare al notify lo user_id(o e-mail) e il msg
                for email in emails:
                    notifiche.append({"email": email[0],"message":message})
                # invioNotifier(result,msg)
            else:
                print("messaggio non destinato a un utente") # qui si potrebbe fare un meccanismo che elimina dal database la tratta, al proposito potrebbe aver senso cancellarla la tratta
        try:
            offset=messages.offset
            offsets = {'Aeroporti': offset + 1} 
            consumer_aeroporto.commit(offsets)
        except Exception as e:
            print("Commit failed due to : ", e)
        invioNotifier(notifiche)


if __name__ == "__main__":
    # Creazione del primo thread
    t1 = threading.Thread(target=leggi_topic_tratte)

    # Creazione del secondo thread
    t2 = threading.Thread(target=leggi_topic_aeroporti)

    # Avvio dei thread
    t1.start()
    t2.start()


