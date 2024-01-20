from prometheus_api_client import PrometheusConnect
from flask import Flask, jsonify, request
import requests
import sqlite3
import mysql.connector
import os
#tempo di risposta di ogni api e consumo di risorse
#response time e consumo di cpu
#misura a rules
app=Flask(__name__)

try:
    conn = mysql.connector.connect(user='user', password=os.environ.get("MYSQL_ROOT_PASSWORD_POST_DB"), host='localhost', database='metrics')
    cursor = conn.cursor()
except mysql.connector.errors as e:
    print(f"Errore durante l'esecuzione della query: {e}")

#da sistemare le soglie
metrics = [
    {'nome': 'node_network_receive_errs_total', 'soglia': 10, 'desiderato': 5},
    {'nome': 'node_network_transmit_errs_total', 'soglia': 10, 'desiderato': 5},
    {'nome': 'node_memory_MemAvailable_bytes', 'soglia': 10, 'desiderato': 5},
    {'nome': 'node_ipvs_connection_total', 'soglia': 10, 'desiderato': 5},
    {'nome': 'node_ipvs_incoming_bytes_total', 'soglia': 10, 'desiderato': 5},
    {'nome': 'node_ipvs_incoming_packets_total', 'soglia': 10, 'desiderato': 5},
    {'nome': 'node_ipvs_outgoing_bytes_total', 'soglia': 10, 'desiderato': 5},
    {'nome': 'node_ipvs_outgoing_packets_total', 'soglia': 10, 'desiderato': 5}
]

for metric in metrics:
    try:
        cursor.execute('''
        INSERT INTO metriche (nome, soglia, desiderato)
        VALUES (?, ?, ?)
        ''', (metric['nome'], metric['soglia'], metric['desiderato']))
        conn.commit()
    except mysql.connector.errors as e:
        print(f"Errore durante l'esecuzione della query: {e}")

#ritorna la lista dei nomi delle metriche
def get_metrics_list():
    query="SELECT nome FROM metriche"
    cursor.execute(query)
    metriche = cursor.fetchall()
    return metriche

#prende il valore attuale delle metriche
@app.route('/get_valori_attuali', methods=['POST'])
def fetch_prometheus_metrics():
    #query a prometheus con la lista di metriche
    metrics_list=get_metrics_list()
    query = ', '.join(metrics_list) #sistema
    prometheus_url="http://prometheus:9090"
    # Crea un'istanza di PrometheusConnect con l'URL del tuo server Prometheus
    prom = PrometheusConnect(url=prometheus_url, disable_ssl=True)
    # Esegui la query per ottenere le metriche specifiche
    result = prom.custom_query(query)
    # Restituisci i risultati della query
    return result

#ritorna i valori desiderati delle metriche
@app.route('/get_valori_desiderati', methods=['POST'])
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
@app.route('/get_stato_attuale', methods=['POST'])
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

@app.route('/elimina_metrica', methods=['POST'])
def elimina_metrica():
    if request.method == 'POST': 
        data = request.json
        try:
            query="DELETE FROM metriche WHERE nome=?"
            cursor.execute(query,(data['nome'],))
            conn.commit()
        except mysql.connector.errors as e:
            print(f"Errore durante l'esecuzione della query: {e}")
            return e
        return "metrica eliminata"
    
@app.route('/aggiungi_metrica', methods=['POST'])
def aggiungi_metrica():
    if request.method == 'POST': 
        data = request.json
        try:
            cursor.execute('''
            INSERT INTO metriche (nome, soglia, desiderato)
            VALUES (?, ?, ?)
            ''', (data['nome'], data['soglia'], data['desiderato']))
            conn.commit()
        except mysql.connector.errors as e:
            print(f"Errore durante l'esecuzione della query: {e}")
            return e
        return "metrica aggiunta"

#con menu, ma dovrebbe essere più giusto con la route, come sopra
'''
#aggiunge o rimuove metriche ad SLA TO_DO probabilmente così non va bene e devo farlo con la route
def aggiorna_metriche():
    print("Ecco le metriche attuali del SLA \n")
    metric_list=get_metrics_list()
    print(metric_list)
    scelta=int(input("Inserisci 1 se vuoi eliminare una metrica, 2 se vuoi aggiungerla, qualsiasi altro numero se vuoi uscire "))
    if scelta==1:
        nome=input("Scrivi il nome della metrica da eliminare ")
        query="DELETE FROM metriche WHERE nome=?"
        cursor.execute(query,(nome,))
        conn.commit()
    elif scelta==2:
        nome=input("Scrivi la metrica da aggiungere ")
        soglia=input("Scrivi la soglia della metrica da aggiungere ")
        desiderato=input("Scrivi il valore desiderato della metrica da aggiungere ")
        cursor.execute('''
        #INSERT INTO metriche (nome, soglia, desiderato)
        #VALUES (?, ?, ?)
        #''', (nome, soglia, desiderato))
        #conn.commit()
    #else:
    #    return "Non hai eliminato nè aggiunto niente"

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5014, debug=True, threaded=True) #vedi numero porta
