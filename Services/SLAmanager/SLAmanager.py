import time
from prometheus_api_client import PrometheusConnect, MetricRangeDataFrame, PrometheusApiClientException
from flask import Flask, jsonify, request
import mysql.connector
import os
from datetime import datetime, timedelta
import numpy as np
import statsmodels.api as sm
#from scipy.stats import norm
#from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
# from pyramid.arima import auto_arima
from chart_studio import plotly
import plotly.graph_objs as go
from pmdarima import auto_arima
from sklearn.metrics import mean_squared_error
from statsmodels.tools.eval_measures import rmse
import cufflinks as cf
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing

app=Flask(__name__)

# while(True):
#     try:
#         conn = mysql.connector.connect(user='root', password='password', host='mysql', database='metrics')
#         cursor = conn.cursor()
#         break
#     except mysql.connector.Error as e:
#         print(f"Errore durante l'esecuzione della query: {e}")
#         time.sleep(10)

prometheus_url="http://prometheus-service:9090"
metriche_personalizzate = ['scraping_time','elaborating_tratte_time','elaborating_aeroporti_time']

def contains(data,lista):
    return data in lista
    # for metrica in lista:
    #     if data==metrica:
    #         return True
    # return False

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
    return valori

#prende il valore attuale delle metriche
@app.route('/get_valori_attuali', methods=['POST'])
def fetch_prometheus_metrics():
    try:
        queries=get_metrics_list()
        prom = PrometheusConnect(url=prometheus_url, disable_ssl=True)
        # Esegui la query per ottenere le metriche specifiche
        result={}
        for query in queries:
          result[query]=prom.custom_query(query)
          if result[query]==[]:
            result[query]="campioni insufficienti"
        # Restituisci i risultati della query
        return result
    except PrometheusApiClientException as e:
        print(f"Errore durante l'esecuzione della query: {e}")

#permette di eliminare una metrica dal SLA set
@app.route('/elimina_metrica', methods=['POST'])
def elimina_metrica():
    if request.method == 'POST': 
        data = request.json
        if not contains(data['nome'],metriche_personalizzate):
            try:
                query="DELETE FROM metriche WHERE nome=%s"
                cursor.execute(query,(data['nome'],))
                conn.commit()
            except mysql.connector.errors as e:
                print(f"Errore durante l'esecuzione della query: {e}")
                return e
            return "metrica eliminata"
        else:
            return "impossibile eliminare metrica personalizzata"

#permette di aggiungere una metrica dal SLA set    
@app.route('/aggiungi_metrica', methods=['POST'])
def aggiungi_metrica():
    if request.method == 'POST': 
        data = request.json
        try:
            prom = PrometheusConnect(url=prometheus_url, disable_ssl=True)
            result=prom.custom_query(data['nome'])
            if result!=[]:
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
            else:
                return "metrica inesistente"
        except PrometheusApiClientException as e:
            print(f"Errore durante l'esecuzione della query: {e}")

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
    return metriche

#ritorna se c'è stata violazione o no per ogni metrica
@app.route('/get_stato_attuale', methods=['POST'])
def get_violazioni():
    violazioni={}
    valori=fetch_prometheus_metrics()
    #scorro sia la chiave che il valore del mio dizionario
    for metrica,valore in valori.items():
        try:
            print("valore attuale ",valore,"\n")
            nome_metrica=metrica
            query="SELECT soglia FROM metriche WHERE nome=%s"
            cursor.execute(query, (nome_metrica,))
            value = cursor.fetchone()
            cursor.reset()
            if float(valore[0]["value"][1])>value[0]:
                violazioni[nome_metrica]=True
            else:
                violazioni[nome_metrica]=False
        except mysql.connector.Error as e:
            print(f"Errore durante l'esecuzione della query: {e}")
            return e
        except Exception as e:
            print(f"Errore durante l'esecuzione : {e}")
            return e
    return violazioni

#ritorna il numero di violazioni in un arco di tempo
@app.route('/get_violazioni_tempo', methods=['POST'])
def get_violazioni_tempo():
    if request.method == 'POST': 
        data = request.json #viene passato come argomento le ore desiderate
        violazioni={}
        # Connessione a Prometheus
        prom = PrometheusConnect(url=prometheus_url)
        try:
            query="SELECT nome, soglia FROM metriche"
            cursor.execute(query)
            metriche = cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Errore durante l'esecuzione della query: {e}")
        for metrica in metriche: 
            try:
                query= f'sum_over_time(count({metrica[0]} > {metrica[1]})[{data["ore"]}h:])'
                # query = f'count_over_time((rate({metrica[0]}[1h:]) > {metrica[1]})[1h:])'
                # result = prom.custom_query_range(query, start_time=start, end_time=end, step='1h')
                result=prom.custom_query(query)
                print("risultato ",query," ",result,"\n")
                if result!=[]:
                    count = result[0]['value'][1]
                    print("risultato ",query," ",result,"\n")
                    violazioni[metrica[0]]=count
                else:
                    violazioni[metrica[0]]="0"
            except PrometheusApiClientException as e:
                print(f"Errore durante l'esecuzione della query prometheus : {e}")
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
    # probabilities={}
    # if request.method == 'POST': 
    #     data = request.json
    #     end=datetime.utcnow()
    #     start=end-timedelta(minutes=10) #TO_DO vedi se così è giusto
    #     #chiedo a prometheus i valori delle metriche negli ultimi 10 minuti
    #     queries=get_metrics_list()
    #     for query in queries:
    #         try:
    #           prom = PrometheusConnect(url=prometheus_url)
    #           response=prom.custom_query_range(query, start_time=start, end_time=end, step="5s")
    #           print("response ",response,"\n")
    #           #TO_DO da sistemare qui, si devono prendere tutti i valori
    #           #metric_data = response['data']['result']
    #           metric_data_string = response[0]['values']
    #           metric_data = [[sublist[0], float(sublist[1])] for sublist in metric_data_string]
    #           print("data ",metric_data,"\n")
    #           #for entry in metric_data:
    #           #modo con ExponentialSmoothing
    #           metric_name = query
    #           # Estraggo i dati specifici per la metrica corrente
    #           #TO_DO devo prendere la lista, non un unico valore,forse senza [0]
    #           #metric_values = metric_data[0]['values'][1]
    #           #metric_values = metric_data[1]
    #           #metric_values = [sublist[1] for sublist in metric_data]
    #           #print("array valori ",metric_values,"\n")
    #           # Converti i dati delle metriche in un DataFrame pandas
    #           df = pd.DataFrame(metric_data, columns=['timestamp', 'value'])
    #           df['timestamp'] = pd.to_datetime(df['timestamp'])
    #           df.set_index('timestamp', inplace=True)
    #           # Ordina i dati per il timestamp, potrebbe non essere necessario a seconda della risposta di Prometheus
    #           df.sort_index(inplace=True)
    #           # Applico ExponentialSmoothing
    #           tsmodel = ExponentialSmoothing(df['value'].interpolate(),trend='add', seasonal='add', seasonal_periods=5).fit()
    #           # Fai previsioni per i prossimi n periodi
    #           forecast_steps = round((data['minuti']*60) / 5)
    #           forecast = tsmodel.forecast(steps=forecast_steps)
    #           #prendo la soglia della data metrica
    #           try:
    #               query="SELECT soglia FROM metriche WHERE nome= %s"
    #               cursor.execute(query, (metric_name,)) #vedi se è giusto
    #               threshold = cursor.fetchone()
    #           except mysql.connector.errors as e:
    #               print(f"Errore durante l'esecuzione della query: {e}")
    #               return e
    #           #calcolo la probabilità
    #           threshold=threshold[0]
    #           violations = sum(forecast > threshold)
    #           probability_of_violation = violations / len(forecast)
    #           #lo aggiungo al dizionario di probabilities
    #           probabilities[metric_name]=probability_of_violation

    #         except PrometheusApiClientException as e:
    #           print(f"Errore durante l'esecuzione della query prometheus : {e}")
    #     #finito per ogni metrica ritorno il dizionario
    #     return probabilities

        # Visualizza i dati originali e le previsioni

    #ARIMA PROVA

    if request.method == 'POST': 
        data = request.json
        end=datetime.now()
        start=end-timedelta(minutes=10) #TO_DO vedi se così è giusto
        start_test=start-timedelta(minutes=60)#2880
        end_test=start
        query="node_memory_MemAvailable_bytes"
        try:
            prometheus_url="http://localhost:9090"
            prom = PrometheusConnect(url=prometheus_url)
            response=prom.custom_query_range(query, start_time=start, end_time=end, step="15s")#30m
            response_test=prom.custom_query_range(query, start_time=start_test, end_time=end_test, step="15s") #30m 
        except PrometheusApiClientException as e:
            print(f"Errore durante l'esecuzione della query prometheus : {e}")
            return "Errore connessione prometheus"
        if response ==[] or response_test ==[]:
            return "campioni insufficienti, riprovare in seguito"
        metric_data_string = response[0]['values']
        metric_data = [[sublist[0], float(sublist[1])] for sublist in metric_data_string]
        metric_data_string_test = response_test[0]['values']
        metric_data_test = [[sublist[0], float(sublist[1])] for sublist in metric_data_string_test]

            # Converti i dati delle metriche in un DataFrame pandas
        df = pd.DataFrame(metric_data, columns=['timestamp', 'value'])
        df['timestamp'] = pd.to_datetime(df['timestamp'],unit='s')
        #prometheus mi torna i valori con fuso orario UTC passo al nostro
        df['timestamp'] = df['timestamp'] + timedelta(hours=1)
        df.set_index('timestamp', inplace=True)
        # Ordina i dati per il timestamp
        df.sort_index(inplace=True)
        df = df.asfreq('15s')#1min
        df.dropna(inplace=True)
        # print("test \n",metric_data_test)
        metric_data_test = np.array(metric_data_test)
        metric_data_test = metric_data_test.reshape(-1, 2)
        df_train = pd.DataFrame(metric_data_test, columns=['timestamp', 'value'])
        df_train['timestamp'] = pd.to_datetime(df_train['timestamp'],unit='s')
        #prometheus mi torna i valori con fuso orario UTC passo al nostro
        df_train['timestamp'] = df_train['timestamp'] + timedelta(hours=1)
        df_train.set_index('timestamp', inplace=True)
        df_train = df_train.asfreq('15s')#1min
        df_train.dropna(inplace=True)
        # Ordina i dati per il timestamp
        df_train.sort_index(inplace=True)
        print("df_train ",df_train)
        print("df ",df)
        # print("train\n",df_train)
        # print("lunghezza ",len(df_train))
        result = seasonal_decompose(df_train, model='additive', period=int(len(df_train)/2))
        # trend = result.trend.dropna()
        # fig = go.Figure()
        # fig.add_scatter(y=trend, x=df_train.index)
        # fig.show()
        # Detrendizzazione della serie temporale

        stepwise_model = auto_arima(df_train, start_p=1, start_q=1,
                    max_p=3, max_q=5, m=10,
                    start_P=0, seasonal=True,
                    d=1, D=1, trace=True,
                    error_action='ignore',  
                    suppress_warnings=True, 
                    stepwise=True)
                    # trend=trend)


        stepwise_model.fit(df_train)
        future_forecast = stepwise_model.predict(n_periods=len(metric_data_test),dynamic=False, typ='levels')
        future_forecast = pd.DataFrame(future_forecast,index = df.index,columns=['Prediction'])
        # print("index 1 ",df.index)
        # print("date forecast ",future_forecast)
        df_comparazione=pd.concat([df,future_forecast],axis=1)
        # print("concat\n",df_comparazione)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_comparazione.index, y=df_comparazione['value'], mode='lines', name='Reale'))
        fig.add_trace(go.Scatter(x=df_comparazione.index, y=df_comparazione['Prediction'], mode='lines', name='future_forecast'))

        fig.update_layout(
            title="Reale+predizione",
            xaxis_title="Tempo",
            yaxis_title="Valore"
        )
        fig.show()
        df_trained = df.merge(df_train, left_index=True, right_index=True, how='outer')
        df_trained = df.combine_first(df_train)
        # df_trained.drop("value_y",axis=1)  
        # df_trained.set_index('timestamp', inplace=True)
        # print("trained ",df_trained)
        # df_trained_shaped = np.array(df_trained)   
        # df_trained_shaped = df_trained_shaped.reshape(-1)
        # print("df shaped ",df_trained_shaped )
        df_trained = df_trained.asfreq('15s')#1min
        df_trained.dropna()
        df_trained.sort_index(inplace=True)
        print("df_trained ",df_trained)
        stepwise_model=auto_arima(df_trained, start_p=1, start_q=1,
                    max_p=3, max_q=5, m=10,
                    start_P=0, seasonal=True,
                    d=1, D=1, trace=True,
                    error_action='ignore',  
                    suppress_warnings=True, 
                    stepwise=True)
        stepwise_model.fit(df_trained)
        print("df_trained ",df_trained)
        timestamp = pd.date_range(start=end, end=end+timedelta(minutes=data["minuti"]), freq='15s')
        lista=[]
        now=int((end-datetime(1970,1,1)).total_seconds())
        # now = math.ceil(now)
        print("inzio ",end)
        for i in range(0, data["minuti"]*60+15, 15):
            # Ottieni il timestamp corrente e convertilo in secondi totali
            now = now+15
            # Aggiungi il totale di secondi alla lista
            lista.append([now,0])
        list_of_lists = [[date.date(),0] for date in timestamp]
        # print("list ",lista)
        timestamp_index = pd.DataFrame(lista, columns=['timestamp','value'])
        timestamp_index['timestamp'] = pd.to_datetime(timestamp_index['timestamp'],unit='s')
        timestamp_index.set_index('timestamp', inplace=True)
        timestamp_index = timestamp_index.asfreq('15s')#1min
        timestamp_index.dropna(inplace=True)
        # Ordina i dati per il timestamp
        timestamp_index.sort_index(inplace=True)
        # timestamp = pd.date_range(start=end,end=end+timedelta(minutes=data['minuti']),freq='15s')
        future_forecast = stepwise_model.predict(n_periods=len(timestamp),dynamic=False, typ='levels')
        print("future ",future_forecast)
        # future_forecast = pd.DataFrame(future_forecast,index = timestamp_index.index ,columns=['Prediction'])
        future_forecast = pd.DataFrame(future_forecast, columns=['Prediction'])
        # Impostazione dell'indice
        future_forecast.index = timestamp_index.index
        print("future 2 ",future_forecast)
        #future_forecast = pd.DataFrame(future_forecast,index = df.index,columns=['Prediction'])
        fig = go.Figure()
        fig.add_scatter(y=future_forecast["Prediction"], x=future_forecast.index)
        fig.update_layout(
            title="nuova predizione",
            xaxis_title="Tempo",
            yaxis_title="Predizione"
        )
        fig.show()
        violations=0
        for value in future_forecast["Prediction"]:
            if value > 884879400: #soglia metrica memoria disponibile presa in considerazione
                violations=violations+1
        probability_of_violation = violations / len(future_forecast["Prediction"])
        return f"probabilità violazione nei prossimi {data['minuti']} minuti = {probability_of_violation}%"

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5014, debug=True, threaded=True)
