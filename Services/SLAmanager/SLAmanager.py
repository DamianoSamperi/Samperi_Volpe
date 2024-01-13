from prometheus_client import CollectorRegistry, Gauge, write_to_textfile
from flask import Flask, jsonify, request
import requests

app=Flask(__name__)

def fetch_prometheus_metrics():
    node_exporter_url = "http://localhost:9100" #si deve mettere il nome del container
    output_file_path = "metrics.txt" #noi dobbiamo inserirli in un database
    # URL dell'endpoint di Node Exporter che esporta le metriche
    metrics_url = f"{node_exporter_url}/metrics"

    # Effettua una richiesta HTTP per ottenere le metriche
    response = requests.get(metrics_url)

    if response.status_code == 200:
        # Crea un oggetto `CollectorRegistry` per registrare le metriche
        registry = CollectorRegistry()

        #esempio con cpu_usage, noi non dobbiamo usare questo
        cpu_usage = Gauge('cpu_usage', 'CPU Usage Percentage', registry=registry)
        for line in response.text.split('\n'):
            if line.startswith('cpu_usage'):
                cpu_usage.set(float(line.split()[1]))

        # Scrivi le metriche su un file di testo nel formato Prometheus
        write_to_textfile(output_file_path, registry)
        print(f"Metriche scritte su {output_file_path}")
    else:
        print(f"Errore durante il recupero delle metriche. Codice di stato: {response.status_code}")

#aggiunge o rimuove metriche ad SLA
def aggiorna_metriche():
    return

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
