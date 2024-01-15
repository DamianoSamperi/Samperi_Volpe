from prometheus_api_client import PrometheusConnect
from flask import Flask, jsonify, request
import requests
import sqlite3

app=Flask(__name__)
#lista delle metriche d'interesse
#TO_DO da selezionare valori desiderati e valori soglia e inserire tutto nel database
metric_list=['node_network_receive_errs_total', 'node_network_transmit_errs_total',
                  'node_memory_MemAvailable_bytes', 'node_ipvs_connection_total',
                  'node_ipvs_incoming_bytes_total', 'node_ipvs_incoming_packets_total',
                  'node_ipvs_outgoing_bytes_total', 'node_ipvs_outgoing_packets_total']

try:
    conn = sqlite3.connect('metrics.db',check_same_thread=False)
    cursor = conn.cursor()
except sqlite3.Error as e:
    print(f"Errore durante la connessione al database: {e}")

try:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metriche (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            valore TEXT NOT NULL,
            soglia TEXT NOT NULL,
            desiderato TEXT NOT NULL
        )
    ''')
except sqlite3.Error as e:
    print(f"Errore durante l'esecuzione della query: {e}")

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
    return

#ritorna se c'è stata violazione o no per ogni metrica
def get_violazioni():
    return

#ritorna il numero di violazioni in un arco di tempo
def get_violazioni_tempo():
    return

#ritorna la probabilità che ci sia una violazione nel prossimo intervallo di tempo x
def get_probabilità_violazioni():
    return



if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5014, debug=True, threaded=True) #vedi numero porta
