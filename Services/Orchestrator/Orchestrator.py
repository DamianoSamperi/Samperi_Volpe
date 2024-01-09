from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)

def compensa_registrazione_tratta_rules(data): #qui viene eliminata la tratta non riuscita
    url = 'http://rules:5005/elimina_tratte_rules'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=data, headers=headers)
    Count = {"count":response}
    if Count!=-1:
        return "errore durante l'inserimento della tratta, riprova"
    
def compensa_registrazione_aeroporto_rules(data): #qui viene eliminato l'aeroporto' non riuscito
    url = 'http://rules:5005/elimina_aeroporto_rules'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=data, headers=headers)
    Count = {"count":response}
    if Count!=-1:
        return "errore durante l'inserimento dell'aeroporto, riprova"
    

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
            compensa_registrazione_aeroporto_rules(data)
        

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5013, debug=True, threaded=True)