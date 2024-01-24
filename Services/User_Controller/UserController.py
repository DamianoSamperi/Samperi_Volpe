from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)         

def autentica_client(email):
    url = 'http://users-service:5001/controlla_utente'
    params = {'email': email}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            user=response.json()["userid"]
            if user==False:
                print("non sei registrato")
                return user
            else:
                print("ok esisti")
                return user
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def trova_email_by_tratta(ori,dest,pr,adulti):
    url='http://rules-service:5005/trova_email_by_tratta_rules'
    result = requests.post(url, json={'ori':ori, 'dest': dest,'pr': pr, 'adulti':adulti}) #aggiunti adulti
    print("result rules ",result.json())
    return result.json()

def trova_email_by_offerte(ori,pr):
    url='http://rules-service:5005/trova_email_by_aeroporti_rules'
    result = requests.post(url, json={'ori':ori,'pr':pr})
    return result.json()

def invia_tratta(origine, destinazione, adulti, id):
    url = 'http://controllertratta-service:5002/ricevi_tratte_usercontroller'
    payload = {'origine': origine, 'destinazione': destinazione, 'adulti': adulti}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    # Stampa la risposta ricevuta dal servizio
    print("risposta ",response.status_code)
    if response.status_code!=200:
        url = 'http://rules-service:5005/elimina_tratte_Rules'
        payload = {'userid': id, 'origine': origine, 'destinazione': destinazione, 'adulti': adulti}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        return "non è stato possibile registrarsi"
    print(response.text)
    return "iscrizione effettuata"

def invia_aeroporto(aeroporto, id):
    url = 'http://controllertratta-service:5002/ricevi_aeroporto_usercontroller'
    payload = {'aeroporto': aeroporto}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    # Stampa la risposta ricevuta dal servizio
    print(response.status_code)
    if response.status_code!=200:
        url = 'http://rules-service:5005/elimina_aeroporto_Rules'
        payload = {'userid': id, 'origine': aeroporto}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        return "non è stato possibile registrarsi"
    print(response.text)
    return "iscrizione effettuata"

#FLASK----------------------------------------------------------------------------------
@app.route('/trova_email_by_tratta', methods=['POST'])
def trova_email_tratta():
    if request.method == 'POST':
        data = request.json 
        print("data normali",data)
        result=trova_email_by_tratta(data["ori"],data["dest"],data["pr"],data["adulti"]) #aggiunti adulti
        print("result normali",result)
        return result
    
@app.route('/trova_email_by_offerte', methods=['POST'])
def trova_email_offerte():
    if request.method == 'POST':
        data = request.json
        result=trova_email_by_offerte(data["ori"],data["pr"])
        return result
    
@app.route('/registrazione', methods=['POST'])
def registra_client():
    data= request.json
    #prima controllo se era già registrato
    autenticato =autentica_client(data["email"])
    if  autenticato == False:
        url = 'http://users-service:5001/registra_utente'
        payload = {'email': data["email"], 'nome': data["nome"], 'cognome': data["cognome"]}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        # Stampa la risposta ricevuta dal servizio
        if response.status_code == 200:
            return response.json()["message"]
        else:
            return "errore nella registrazione"
    elif autenticato != None:
        return "cliente già registrato"
    else:
        return "Errore nella connessione"


@app.route('/Insert_tratta', methods=['POST'])
def inserisci_tratta():
    data= request.json
    email = data["email"]
    origine = data["origine"]
    destinazione = data["destinazione"]
    budget = data["budget"]
    adulti= data["adulti"] #aggiunti adulti
    if type(budget)== int or type(budget)==float: 
        if(adulti>0):
            user=autentica_client(email) 
            if user != False:
                if len(origine)!=3 or len(destinazione)!=3 or origine.isalpha == False or destinazione.isalpha == False:
                    return "i codici degli aeroporti devono avere lunghezza 3 e devono essere letterali"
                else:
                    url = 'http://rules-service:5005/ricevi_tratte_Rules'
                    payload = {'userid': user[0], 'origine': origine, 'destinazione': destinazione, 'budget': budget, 'adulti': adulti} #aggiunti adulti
                    headers = {'Content-Type': 'application/json'}
                    response = requests.post(url, json=payload, headers=headers)
                    print("response count ",response.json()["count"]) 
                    if response.json()["count"]!=-1:
                        if response.json()["count"]==1: #la invia solo è il primo cliente ad averla chiesta
                            print("sto inviando")
                            riuscito=invia_tratta(origine,destinazione,adulti,user[0])
                        return riuscito 
                    else:
                        return "Errore durante l'iscrizione"     
            return "autenticazione fallita, si prega di registrarsi"
        else:
            return "inserire un numero di adulti valido"
    else:
        return "inserire un budget valido"


@app.route('/Insert_aeroporto', methods=['POST'])
def inserisci_aeroporto():
    data= request.json
    email = data["email"]
    origine = data["origine"]
    budget = data["budget"]
    if type(budget)== int or type(budget)==float: 
        user=autentica_client(email)
        if user != False:
            if len(origine)!=3 or origine.isalpha == False:
                return "i codici degli aeroporti devono avere lunghezza 3 e devono essere letterali"
            else:
                url = 'http://rules-service:5005/ricevi_aeroporti_Rules'
                payload = {'userid': user[0], 'origine': origine, 'budget': budget}
                headers = {'Content-Type': 'application/json'}
                response = requests.post(url, json=payload, headers=headers)
                #print(response.status_code) forse devo controllare lo status_code
                if response.json()["count"]!=-1:
                    if response.json()["count"]==1: #la invia solo se è il primo cliente ad averla chiesta
                        riuscito=invia_aeroporto(origine,user[0])
                    return riuscito
                else:
                    return "Errore durante l'iscrizione"   
        return "autenticazione fallita, si prega di registrarsi"
    else:
        return "inserire un budget valido"

@app.route('/Disiscrizione_tratta', methods=['POST'])
def disiscrizione_tratta():
    data= request.json
    email = data["email"]
    origine = data["origine"]
    destinazione = data["destinazione"]
    adulti= data["adulti"]
    user=autentica_client(email) 
    if user != False:
        if len(origine)!=3 or len(destinazione)!=3 or origine.isalpha == False or destinazione.isalpha == False:
            return "i codici degli aeroporti devono avere lunghezza 3 e devono essere letterali"
        else:
            url = 'http://rules-service:5005/elimina_tratte_Rules'
            payload = {'userid': user[0], 'origine': origine, 'destinazione': destinazione, 'adulti': adulti}
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)
            #print(response.status_code) forse devo controllare lo status_code
            #return response.json()
            if response.json()["count"]!=-1:
                if  response.json()["count"]==0: #la invia per eliminarla solo se è 0 il count di persone iscritte
                    invia_tratta(origine,destinazione,adulti)
            else:
                return "Utente non registrato a questa tratta" 
            #if response.json()[0]==0:
            #    return "nessuna tratta corrispondente trovata"
            return "Disiscrizione effettuata"
    return "autenticazione fallita, si prega di registrarsi"

@app.route('/Disiscrizione_aeroporto', methods=['POST'])
def disiscrizione_aeroporto():  
    data= request.json
    email = data["email"]
    origine = data["origine"]
    user=autentica_client(email) 
    if user != False:
        if len(origine)!=3 or origine.isalpha == False:
            return "i codici degli aeroporti devono avere lunghezza 3 e devono essere letterali"
        else:
            url = 'http://rules-service:5005/elimina_aeroporto_Rules'
            payload = {'userid': user[0], 'origine': origine}
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)
            #print(response.status_code) forse devo controllare lo status_code
            if response.json()["count"]!=-1:
                if response.json()["count"]==0: #la invia per eliminarla solo se è 0 il count di persone iscritte
                    invia_aeroporto(origine)  
            else:
                return "Utente non registrato a questo aeroporto" 
            #if response.json()["trovati"]==0:
            #    return "nessun aeroporto corrispondente trovato"    
            return "Disiscrizione effettuata"
    return "autenticazione fallita, si prega di registrarsi"




if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000, debug=True, threaded=True)