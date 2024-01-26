import time
from prometheus_api_client import PrometheusConnect, MetricRangeDataFrame, PrometheusApiClientException
from flask import Flask, jsonify, request
import mysql.connector
import os
from datetime import datetime, timedelta
#import numpy as np
#from scipy.stats import norm
#from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
#import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
#tempo di risposta di ogni api e consumo di risorse
#response time e consumo di cpu
#misura a rules
app=Flask(__name__)

while(True):
    try:
        conn = mysql.connector.connect(user='root', password='password', host='mysql', database='metrics')
        cursor = conn.cursor()
        break
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
        time.sleep(10)

prometheus_url="http://prometheus-service:9090"
#da sistemare le soglie
metrics = [
    {'nome': 'node_network_receive_errs_total', 'soglia': 2, 'desiderato': 0},
    {'nome': 'node_network_transmit_errs_total', 'soglia': 2, 'desiderato': 0},
    {'nome': 'node_memory_MemAvailable_bytes', 'soglia': 884879400, 'desiderato': 884879360},
    {'nome': 'node_ipvs_connections_total', 'soglia': 10, 'desiderato': 5}, #vedi
    {'nome': 'node_ipvs_incoming_bytes_total', 'soglia': 10, 'desiderato': 5}, #vedi
    {'nome': 'node_ipvs_incoming_packets_total', 'soglia': 10, 'desiderato': 5}, #vedi
    {'nome': 'node_ipvs_outgoing_bytes_total', 'soglia': 10, 'desiderato': 5}, #vedi
    {'nome': 'node_ipvs_outgoing_packets_total', 'soglia': 10, 'desiderato': 5} #vedi
]

#TO_DO forse conviene che inseriamo le metriche base direttamente nello script sql
delete_query = f'DELETE FROM metriche'
cursor.execute(delete_query)
conn.commit()

for metric in metrics:
    try:
        cursor.execute('''
        INSERT INTO metriche (nome, soglia, desiderato)
        VALUES (%s, %s, %s)
        ''', (metric['nome'], metric['soglia'], metric['desiderato']))
        conn.commit()
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")

#ritorna la lista dei nomi delle metriche
@app.route('/get_sla', methods=['POST'])
def get_metrics_list():
    try:
        query="SELECT nome FROM metriche"
        cursor.execute(query)
        metriche = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
    valori = [tupla[0] for tupla in metriche]
    # metriche = ', '.join(valori) TO_DO che senso ha?
    return valori

#prende il valore attuale delle metriche
@app.route('/get_valori_attuali', methods=['POST'])
def fetch_prometheus_metrics():
    try:
        #query a prometheus con la lista di metriche
        queries=get_metrics_list()
        prom = PrometheusConnect(url=prometheus_url, disable_ssl=True)
        # Esegui la query per ottenere le metriche specifiche
        result=[]
        for query in queries:
          result.append(prom.custom_query(query))
        # Restituisci i risultati della query
        return result
    except PrometheusApiClientException as e:
        print(f"Errore durante l'esecuzione della query: {e}")

#permette di eliminare una metrica dal SLA set
@app.route('/elimina_metrica', methods=['POST'])
def elimina_metrica():
    if request.method == 'POST': 
        data = request.json
        try:
            query="DELETE FROM metriche WHERE nome=%s"
            cursor.execute(query,(data['nome'],))
            conn.commit()
        except mysql.connector.errors as e:
            print(f"Errore durante l'esecuzione della query: {e}")
            return e
        return "metrica eliminata"

#permette di aggiungere una metrica dal SLA set    
@app.route('/aggiungi_metrica', methods=['POST'])
def aggiungi_metrica():
    if request.method == 'POST': 
        data = request.json
        try:
            cursor.execute('''
            INSERT INTO metriche (nome, soglia, desiderato)
            VALUES (%s, %s, %s)
            ''', (data['nome'], data['soglia'], data['desiderato']))
            conn.commit()
        except mysql.connector.errors as e:
            print(f"Errore durante l'esecuzione della query: {e}")
            return e
        return "metrica aggiunta"

#ritorna i valori desiderati delle metriche
@app.route('/get_valori_desiderati', methods=['POST'])
def get_valori_desiderati():
    try:
        query="SELECT nome, desiderato FROM metriche"
        cursor.execute(query)
        metriche = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
        return e
    return metriche #in teoria va bene così, non penso che devo creare un dizionario

#ritorna se c'è stata violazione o no per ogni metrica
@app.route('/get_stato_attuale', methods=['POST'])
def get_violazioni(): #TO_DO da sistemare in base ai label che mi torna prometheus
    violazioni={}
    valori=fetch_prometheus_metrics()
    #print("valori ritornati da prometheus", valori,"\n")
    for valore in valori:
        try:
            #TO_DO da' problemi, è strano forse il valore che prende, ho provato ma bho
            #lo da' tipo come lista con indice di stringa
            print("valore attuale ",valore,"\n")
            nome_metrica=valore[0]["metric"]["__name__"]
            query="SELECT soglia FROM metriche WHERE nome=%s"
            cursor.execute(query, (nome_metrica,))
            value = cursor.fetchone()
            cursor.reset()
            if float(valore[0]["value"][1])>value[0]: #TO_DO vedi, non so quale dei numeri prende MA OVVIAMENTE TUTTE,QUALE CASPITERINA VUOI
                violazioni[valore[0]["metric"]["__name__"]]=True
            else:
                violazioni[valore[0]["metric"]["__name__"]]=False
        except mysql.connector.Error as e:
            print(f"Errore durante l'esecuzione della query: {e}")
            return e
        except Exception as e:
            print(f"Errore durante l'esecuzione : {e}")
            return e
    return violazioni #forse meglio tornare un json?

#ritorna il numero di violazioni in un arco di tempo
@app.route('/get_violazioni_tempo', methods=['POST'])
def get_violazioni_tempo():
    if request.method == 'POST': 
        data = request.json #viene passato come argomento le ore desiderate
        violazioni={}
        # Connessione a Prometheus
        prom = PrometheusConnect(url=prometheus_url)
        end=datetime.utcnow()
        start=end-timedelta(hours=data['ore']) #vedi se è giusto data["ore"]
        try:
            query="SELECT nome, soglia FROM metriche"
            cursor.execute(query)
            metriche = cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Errore durante l'esecuzione della query: {e}")
        for metrica in metriche:
            # Costruzione della query per ottenere il conteggio delle violazioni
            query = f'count_over_time({metrica[0]} > {metrica[1]})'
            result = prom.custom_query_range(query, start_time=start, end_time=end, step='1h')
            # Estrazione del valore dalla risposta
            count = result[0]['values'][0][1]
            violazioni[metrica["nome"]]=count
        return violazioni
'''
def calculate_probability(predictions, threshold):
    exceeding_values = predictions[predictions > threshold]
    probability = len(exceeding_values) / len(predictions)
    return probability
'''
#ritorna la probabilità che ci sia una violazione nel prossimo intervallo di tempo x
@app.route('/get_probabilità_violazioni', methods=['POST'])
def get_probabilità_violazioni():
    probabilities={}
    if request.method == 'POST': 
        data = request.json
        end=datetime.utcnow()
        start=end-timedelta(minutes=10) #TO_DO vedi se così è giusto
        #chiedo a prometheus i valori delle metriche negli ultimi 10 minuti
        queries=get_metrics_list()
        for query in queries:
            prom = PrometheusConnect(url=prometheus_url)
            response=prom.custom_query_range(query, start_time=start, end_time=end, step="5s")
            metric_data = response['data']['result']
            print(metric_data)
            #for entry in metric_data:
            #modo con ExponentialSmoothing
            metric_name = metric_data[0]['metric']['__name__']
            # Estraggo i dati specifici per la metrica corrente
            #TO_DO devo prendere la lista, non un unico valore,forse senza [0]
            metric_values = metric_data[0]['value'][1] #forse è "values"
            # Converti i dati delle metriche in un DataFrame pandas
            df = pd.DataFrame(metric_values, columns=['timestamp', 'value'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            # Ordina i dati per il timestamp, potrebbe non essere necessario a seconda della risposta di Prometheus
            df.sort_index(inplace=True)
            # Applico ExponentialSmoothing
            tsmodel = ExponentialSmoothing(df['value'].interpolate(),trend='add', seasonal='add', seasonal_periods=5).fit()
            # Fai previsioni per i prossimi n periodi
            forecast_steps = round((data['minuti']*60) / 5)
            forecast = tsmodel.forecast(steps=forecast_steps)
            #prendo la soglia della data metrica
            try:
                query="SELECT soglia FROM metriche WHERE nome= %s"
                cursor.execute(query, (metric_name,)) #vedi se è giusto
                threshold = cursor.fetchone()
            except mysql.connector.errors as e:
                print(f"Errore durante l'esecuzione della query: {e}")
                return e
            #calcolo la probabilità
            treshold=treshold[0]
            violations = sum(forecast > threshold)
            probability_of_violation = violations / len(forecast)
            #lo aggiungo al dizionario di probabilities
            probabilities[metric_name]=probability_of_violation
        #finito per ogni metrica ritorno il dizionario
        return probabilities

        # Visualizza i dati originali e le previsioni
        '''
        plt.plot(df.index, df['value'], label='Original Data')
        plt.plot(pd.date_range(df.index[-1], periods=forecast_steps+1, freq='60s')[1:], forecast, label='Forecast', color='red')
        plt.legend()
        plt.show()
        '''
        #Elio
        '''
        dictPred={}
        metrics=get_metrics_list()
        for name in metrics:
            #rappresenta una query response come un data frame
            #metric_df = MetricRangeDataFrame(Metrics[name])

            data= metric_data.resample(rule='5s').mean(numeric_only="True")

            tsmodel = ExponentialSmoothing(data['value'].interpolate(), trend='add', seasonal='add',seasonal_periods=5).fit()
            
            prediction = tsmodel.forecast(steps=round((10*60)/5))

            # plt.figure(figsize=(24,10))
            # plt.ylabel('Values', fontsize=14)
            # plt.xlabel('Time', fontsize=14)
            # plt.title('Values over time', fontsize=16)
            
            # plt.plot(data, "-", label = 'train')
            # plt.plot(prediction,"--",label = 'pred')
            # plt.legend(title='Series')
            # # plt.show()
            # plt.savefig(fname=name)

            dictPred[name]={"max": prediction.max(),
                        "min": prediction.min(),
                        "avg": prediction.mean()}
        return dictPred
        '''

        #modo con ARIMA
        '''
        # Creo un DataFrame pandas con i dati della metrica
        df = pd.DataFrame(columns=['timestamp'] + metrics)
        for entry in metric_data:
            timestamp = pd.to_datetime(entry['value'][0])
            values = [float(entry['value'][1])]  # Assumendo che il valore della metrica sia un numero
            df = pd.concat([df, pd.DataFrame([timestamp] + values, columns=['timestamp'] + metrics)])

        # Addestramento del modello ARIMA
        for metric in metrics:
            train_data = df[metric]
            model = ARIMA(train_data, order=(1, 1, 1))  # Sostituisci con i tuoi parametri
            fitted_model = model.fit()

            # Previsioni per i prossimi 5 minuti (modifica in base alle tue esigenze)
            forecast_steps = data['minuti']
            future_timestamps = pd.date_range(end_time, periods=forecast_steps+1, freq='60s')[1:]
            predictions = fitted_model.forecast(steps=forecast_steps)

            try:
                query="SELECT soglia FROM metriche WHERE nome= ?"
                cursor.execute(query, (metric,))
                threshold = cursor.fetchone()
            except mysql.connector.errors as e:
                print(f"Errore durante l'esecuzione della query: {e}")
                return e            
            # Calcolo della probabilità di violazione della soglia
            probability = calculate_probability(predictions, threshold)

            probabilities[metric]=probability
        return probabilities
        '''
    
        #modo con media e deviazione standard
        '''
        #calcolo le probabilità di violazioni in base a ciò che ho ottenuto
        probabilities = {}
        for entry in metric_data:
            values = [value[1] for value in entry['values']]
            mean = np.mean(values) #media
            std_dev = np.std(values) #deviazione standard
            try:
                query="SELECT soglia FROM metriche WHERE nome= ?"
                cursor.execute(query, (entry['name'],)) #TO_DO vedi se è name
                threshold = cursor.fetchone()
            except mysql.connector.Error as e:
                print(f"Errore durante l'esecuzione della query: {e}")
                return e
            z_score = (threshold - mean) / std_dev #z-score per la soglia
            #probabilità di violazione usando la distribuzione normale
            probability = norm.cdf(z_score)
            probability_next_interval = 1 - (1 - probability) ** data['minuti']
            probabilities[entry['name']]=probability_next_interval
        return probabilities
        '''

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
