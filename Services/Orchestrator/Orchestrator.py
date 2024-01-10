from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)

#funzione che elimina la tratta non riuscita ad inviare a controller tratte
def compensa_registrazione_tratta_rules(data):
    url = 'http://rules:5005/elimina_tratte_rules'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=data, headers=headers)
    Count = {"count":response}
    if Count!=-1:
        return "errore durante l'inserimento della tratta, riprova"

#funzione che riaggiunge la tratta non riuscita ad eliminare da controller tratte
def compensa_eliminazione_tratta_rules(data):
    url = 'http://rules:5005/ricevi_tratte_rules'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=data, headers=headers)
    Count = {"count":response}
    if Count!=0:
        return "errore durante l'eliminazione della tratta, riprova"  

#funzione che elimina l'aeroporto non riuscito ad inviare a controller tratte
def compensa_registrazione_aeroporto_rules(data):
    url = 'http://rules:5005/elimina_aeroporto_rules'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=data, headers=headers)
    Count = {"count":response}
    if Count!=-1:
        return "errore durante l'inserimento dell'aeroporto, riprova"

#funzione che riaggiunge l'aeroporto non riuscito ad eliminare da controller tratte
def compensa_eliminazione_aeroporto_rules(data):
    url = 'http://rules:5005/ricevi_aeroporti_Rules'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=data, headers=headers)
    Count = {"count":response}
    if Count!=0:
        return "errore durante l'eliminazione della tratta, riprova"  
  

#FLASK---------------------------------------------------------------------------------
@app.route('/ricevi_tratte', methods=['POST'])
def ricevi_tratte():
    if request.method == 'POST': 
        data = request.json 
        url = 'http://rules:5005/ricevi_tratte_Rules'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=data, headers=headers)
        Count = {"count":response}
        return Count #qui non credo ci sia bisogno di una compensazione, perchè nulla
        #è stato aggiunti se tornava errore
    
@app.route('/invia_tratte_controller_tratte', methods=['POST'])
def invia_tratte_controller_tratte():
    if request.method == 'POST': 
        data = request.json 
        try:
            url = 'http://controller_tratta:5002/ricevi_tratte_usercontroller'
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=data, headers=headers)
        except Exception as e:
            #se succede qualcosa compensa l'azione precedente
            errors = json.loads(response.text)
            # Controlla se c'è un campo di errore nella risposta
            if 'error' in errors:
                #se c'è stato un errore durante l'eliminazione
                if errors["error"] == "delete error":
                    compensa_eliminazione_tratta_rules(data)
                #se c'è stato un errore durante l'inserimento
                elif errors["error"] == "insert error":
                    compensa_registrazione_tratta_rules(data)


@app.route('/ricevi_aeroporti', methods=['POST'])
def ricevi_tratte():
    if request.method == 'POST': 
        data = request.json 
        url = 'http://rules:5005/ricevi_aeroporti_Rules'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=data, headers=headers)
        Count = {"count":response}
        return Count #qui non credo ci sia bisogno di una compensazione, perchè nulla
        #è stato aggiunti se tornava errore
    
@app.route('/invia_aeroporti_controller_tratte', methods=['POST'])
def invia_tratte_controller_tratte():
    if request.method == 'POST': 
        data = request.json 
        try:
            url = 'http://controller_tratta:5002/ricevi_aeroporto_usercontroller'
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=data, headers=headers)
        except Exception as e:
            #se succede qualcosa compensa l'azione precedente
            errors = json.loads(response.text)
            # Controlla se c'è un campo di errore nella risposta
            if 'error' in errors:
                #se c'è stato un errore in eliminazione
                if errors["error"] == "delete error":
                    compensa_eliminazione_aeroporto_rules(data)
                #se c'è stato un errore in inserimento
                elif errors["error"] == "insert error":
                    compensa_registrazione_aeroporto_rules(data)
        

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5013, debug=True, threaded=True)