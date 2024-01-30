from kafka import KafkaConsumer,errors
import time
import json
import requests
import threading
import prometheus_client

elaborating_tratte_time = prometheus_client.Gauge('elaborating_tratte_time', 'tempo di elaborazione tratte')
elaborating_aeroporti_time = prometheus_client.Gauge('elaborating_aeroporti_time', 'tempo di elaborazione aeroporti')
elaborating_tratte_time.set(0)
elaborating_aeroporti_time.set(0)
prometheus_client.start_http_server(9998)
# Crea consumatore Kafka per tratte
while True:
    try:
        consumer_tratta = KafkaConsumer('Tratte',
                                bootstrap_servers=['kafka-service:9092'],
                                group_id='grp1',
                                enable_auto_commit=False,
                                value_deserializer=lambda m: json.loads(m.decode('utf-8'))) #quest'ultimo valore da controllare
        print("connesso a broker")
        break
    except errors.NoBrokersAvailable as error:
        print("kafka non disponibile")
        time.sleep(15)

# Crea consumatore Kafka per aeroporti
while True:
    try:            
        consumer_aeroporto = KafkaConsumer('Aeroporti',
                                bootstrap_servers=['kafka-service:9092'],
                                group_id='grp1',
                                enable_auto_commit=False,
                                value_deserializer=lambda m: json.loads(m.decode('utf-8'))) #quest'ultimo valore da controllare
        print("connesso al broker")
        break
    except errors.NoBrokersAvailable as error :
        print("kafka non disponibile")
        time.sleep(15)

def invioNotifier(notifiche):
    response = requests.post('http://notifier-service:5003/recuperomail', json={'notifiche':notifiche})

#istanzio il consumer una sola volta
def leggi_topic_tratte():
    print("sono qui")
    start_time=time.time()
    notifiche_tratta = []
    for messages in consumer_tratta:
        # Ottieni il messaggio dal topic Kafka
        print("ho ricevuto notifiche ",messages.value)
        for message in messages.value:
            result = requests.post('http://user-controller-service:5000/trova_email_by_tratta', json={'ori':message['origin'], 'dest': message['destination'],'pr': message['price'],'adulti': message['adulti'] })
            emails=result.json()
            if emails :
                print(f"esiste almeno un user_id con quelle regole: {emails}")
                for email in emails:
                    notifiche_tratta.append({"email": email[0],"message":message})
        try:      
            consumer_tratta.commit(consumer_tratta.end_offsets.__dict__)
        except Exception as e:
            print("Commit failed due to : ", e)
        if notifiche_tratta:    
            invioNotifier(notifiche_tratta)
            notifiche_tratta=[]
            end_time=time.time()
            elaborating_tratte_time.set(end_time-start_time)


def leggi_topic_aeroporti():
    start_time=time.time()
    notifiche = []
    for messages in consumer_aeroporto:
        print("ho ricevuto notifiche ",messages.value)
        for message in messages.value:
            result = requests.post('http://user-controller-service:5000/trova_email_by_offerte', json={'ori':message['origin'], 'pr': message['price']})
            emails=result.json()
            if emails :
                print(f"esiste almeno un user_id con quelle regole: {emails}")
                for email in emails:
                    notifiche.append({"email": email[0],"message":message})
        try:
            consumer_aeroporto.commit(consumer_aeroporto.end_offsets.__dict__)
        except errors.CommitFailedError as e:
            print("Commit failed due to : ", e)
        if notifiche:
            invioNotifier(notifiche)
            notifiche=[]
            end_time=time.time()
            elaborating_aeroporti_time.set(end_time-start_time)


if __name__ == "__main__":
    # Creazione del primo thread
    t1 = threading.Thread(target=leggi_topic_tratte)

    # Creazione del secondo thread
    t2 = threading.Thread(target=leggi_topic_aeroporti)

    # Avvio dei thread
    t1.start()
    t2.start()


