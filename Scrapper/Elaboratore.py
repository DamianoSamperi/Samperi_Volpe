
from kafka import KafkaConsumer
import sqlite3
import json
import UserController



# Crea un consumatore Kafka
consumer = KafkaConsumer('tratte',
                         bootstrap_servers=['localhost:9092'],
                         value_deserializer=lambda m: json.loads(m.decode('utf-8'))) #quest'ultimo valore da controllare

for message in consumer:
    # Ottieni il messaggio dal topic Kafka
    msg = message.value

    # #  Esegui una query sul database per verificare le informazioni del messaggio
    # cursor.execute("SELECT user_id FROM rules WHERE originLocationCode = ? AND destinationLocationCode= ? AND adults = ?", (msg['originLocationCode'],msg['destinationLocationCode'],msg['adults'],))
    # #potrebbe poi fare una query a User Id per sapere la sua mail e mandare a notify msg e mail
    # result = cursor.fetchone()
    result = UserController.trova_email(msg)
    if result is not None:
        print(f"esiste almeno un user_id con quelle regole: {result}")  #bisogna inviare al notify lo user_id(o e-mail) e il msg
    else:
        print("messaggio non destinato a un utente") # qui si potrebbe fare un meccanismo che elimina dal database la tratta, al proposito potrebbe aver senso cancellarla la tratta 