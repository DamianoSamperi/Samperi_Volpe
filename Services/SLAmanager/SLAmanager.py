from prometheus_api_client import PrometheusConnect
from flask import Flask, jsonify, request
import requests
import sqlite3
import mysql.connector
import os
#tempo di risposta di ogni api e consumo di risorse
#response time e consumo di cpu
app=Flask(__name__)
#lista delle metriche d'interesse
#TO_DO da selezionare valori desiderati e valori soglia e inserire tutto nel database
metric_list=['node_network_receive_errs_total', 'node_network_transmit_errs_total',
                  'node_memory_MemAvailable_bytes', 'node_ipvs_connection_total',
                  'node_ipvs_incoming_bytes_total', 'node_ipvs_incoming_packets_total',
                  'node_ipvs_outgoing_bytes_total', 'node_ipvs_outgoing_packets_total']

#misura a rules

# try:
#     conn = sqlite3.connect('metrics.db',check_same_thread=False)
#     cursor = conn.cursor()
# except sqlite3.Error as e:
#     print(f"Errore durante la connessione al database: {e}")

# try:
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS metriche (
#             nome TEXT PRIMARY KEY NOT NULL,
#             valore TEXT NOT NULL,
#             soglia TEXT NOT NULL,
#             desiderato TEXT NOT NULL
#         )
#     ''')
# except sqlite3.Error as e:
#     print(f"Errore durante l'esecuzione della query: {e}")
try:
    conn = mysql.connector.connect(user='user', password=os.environ.get("MYSQL_ROOT_PASSWORD_POST_DB"), host='localhost', database='metrics')
    cursor = conn.cursor()
except mysql.connector.errors as e:
    print(f"Errore durante l'esecuzione della query: {e}")
#prende il valore attuale delle metriche
def fetch_prometheus_metrics():
    #query a prometheus con la lista di metriche
    query = ', '.join(metric_list)
    prometheus_url="http://prometheus:9090"
    # Crea un'istanza di PrometheusConnect con l'URL del tuo server Prometheus
    prom = PrometheusConnect(url=prometheus_url, disable_ssl=True)
    # Esegui la query per ottenere le metriche specifiche
    result = prom.custom_query(query)
    # Restituisci i risultati della query
    return result

#aggiunge o rimuove metriche ad SLA
def aggiorna_metriche():
    print("Ecco le metriche attuali del SLA \n")
    print(metric_list)
    scelta=int(input("Inserisci 1 se vuoi eliminare una metrica, 2 se vuoi aggiungerla, qualsiasi altro numero se vuoi uscire "))
    if scelta==1:
        elimina=input("Scrivi la metrica da eliminare ")
        #funzione che elimina
    elif scelta==2:
        inserisci=input("Scrivi la metrica da aggiungere ")
        #funzione che aggiunge
    else:
        return "Non hai eliminato nè aggiunto niente"

#ritorna i valori desiderati delle metriche
def get_valori_desiderati():
    try:
        query="SELECT nome, desiderato FROM metriche"
        cursor.execute(query)
        metriche = cursor.fetchall()
    except mysql.connector.errors as e:
        print(f"Errore durante l'esecuzione della query: {e}")
        return e
    return metriche #in teoria va bene così, non penso che devo creare un dizionario

#ritorna se c'è stata violazione o no per ogni metrica
def get_violazioni(): #TO_DO da sistemare in base ai label che mi torna prometheus
    violazioni={}
    valori=fetch_prometheus_metrics()
    for valore in valori:
        try:
            query="SELECT soglia FROM metriche WHERE nome= ?"
            cursor.execute(query, (valore['nome'],))
            value = cursor.fetchone()
            if valore['value']>value:
                violazioni[valore['nome']]=True
            else:
                violazioni[valore['nome']]=False
        except mysql.connector.errors as e:
            print(f"Errore durante l'esecuzione della query: {e}")
            return e
    return violazioni #forse meglio tornare un json?

#ritorna il numero di violazioni in un arco di tempo
def get_violazioni_tempo():
    return

#ritorna la probabilità che ci sia una violazione nel prossimo intervallo di tempo x
def get_probabilità_violazioni():
    return



if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5014, debug=True, threaded=True) #vedi numero porta
