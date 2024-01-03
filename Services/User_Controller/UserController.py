from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)  


# def registra_client(nome,cognome,email):
#     #prima controllo se era già registrato
#     if autentica_client(email) == False:
#         url = 'http://user_controller:5000/registra_utente'
#         payload = {'email': email, 'nome': nome, 'cognome': cognome}
#         headers = {'Content-Type': 'application/json'}
#         response = requests.post(url, json=payload, headers=headers)
#         # Stampa la risposta ricevuta dal servizio
#         print(response.status_code)
#         print(response.json())
#     else:
#         print("cliente già registrato")

# def inserisci_tratta(email, origine, destinazione, budget):
#     user=autentica_client(email) 
#     if user != False:
#         #Rules.inserisci_tratta(user,origine,destinazione,budget)
#         url = 'http://user_controller:5000/ricevi_tratte_Rules'
#         payload = {'userid': user, 'origine': origine, 'destinazione': destinazione, 'budget': budget}
#         headers = {'Content-Type': 'application/json'}
#         response = requests.post(url, json=payload, headers=headers)
#         #print(response.status_code) forse devo controllare lo status_code
#         if response==1: #la invia solo è il primo cliente ad averla chiesta
#             invia_tratta(origine,destinazione)

# def inserisci_aeroporto(email,origine,budget):
#     user=autentica_client(email)
#     if user != False:
#         #Rules.inserisci_aeroporto(user,origine,budget)
#         url = 'http://user_controller:5000/ricevi_aeroporti_Rules'
#         payload = {'userid': user, 'origine': origine, 'budget': budget}
#         headers = {'Content-Type': 'application/json'}
#         response = requests.post(url, json=payload, headers=headers)
#         #print(response.status_code) forse devo controllare lo status_code
#         if response==1: #la invia solo se è il primo cliente ad averla chiesta
#             invia_aeroporto(origine)

# #TO_DO Elena bisogna fare la disiscrizione o come nuova funziona oppure nelle funzione inserisce puoi controllare se gia inserito e in quel caso cancelli dal database e invi al controller solo se non ci sono utenti per quella tratta-aeroporto
# def disiscrizione_tratta(email, origine, destinazione):
#     user=autentica_client(email) 
#     if user != False:
#         #Rules.inserisci_tratta(user,origine,destinazione,budget)
#         url = 'http://user_controller:5000/elimina_tratte_Rules'
#         payload = {'userid': user, 'origine': origine, 'destinazione': destinazione}
#         headers = {'Content-Type': 'application/json'}
#         response = requests.post(url, json=payload, headers=headers)
#         #print(response.status_code) forse devo controllare lo status_code
#         if response==0: #la invia per eliminarla solo se è 0 il count di persone iscritte
#             invia_tratta(origine,destinazione)

# def disiscrizione_aeroporto(email, origine):  
#     user=autentica_client(email) 
#     if user != False:
#         #Rules.inserisci_tratta(user,origine,destinazione,budget)
#         url = 'http://user_controller:5000/elimina_aeroporto_Rules'
#         payload = {'userid': user, 'origine': origine}
#         headers = {'Content-Type': 'application/json'}
#         response = requests.post(url, json=payload, headers=headers)
#         #print(response.status_code) forse devo controllare lo status_code
#         if response==0: #la invia per eliminarla solo se è 0 il count di persone iscritte
#             invia_aeroporto(origine)       

def autentica_client(email):
    url = 'http://users:5001/controlla_utente'
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

def trova_email_by_tratta(ori,dest,pr):
    url='http://rules:5005/trova_email_by_tratta_rules'
    result = requests.post(url, json={'ori':ori, 'dest': dest,'pr': pr})
    print("result rules ",result.json())
    return result.json()

def trova_email_by_offerte(ori,pr):
    url='http://rules:5005/trova_email_by_aeroporti_rules'
    result = requests.post(url, json={'ori':ori,'pr':pr})
    return result.json()

def invia_tratta(origine, destinazione):
    url = 'http://controller_tratta:5002/ricevi_tratte_usercontroller'
    payload = {'origine': origine, 'destinazione': destinazione}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    # Stampa la risposta ricevuta dal servizio
    print(response.status_code)
    print(response.text)

def invia_aeroporto(aeroporto):
    url = 'http://controller_tratta:5002/ricevi_aeroporto_usercontroller'
    payload = {'aeroporto': aeroporto}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    # Stampa la risposta ricevuta dal servizio
    print(response.status_code)
    print(response.text)

#FLASK----------------------------------------------------------------------------------
@app.route('/trova_email_by_tratta', methods=['POST'])
def trova_email_tratta():
    if request.method == 'POST':
        data = request.json 
        print("data normali",data)
        result=trova_email_by_tratta(data["ori"],data["dest"],data["pr"])
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
        url = 'http://users:5001/registra_utente'
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
    if type(budget)== int or type(budget)==float: 
        user=autentica_client(email) 
        if user != False:
            if len(origine)!=3 or len(destinazione)!=3 or origine.isalpha == False or destinazione.isalpha == False:
                return "i codici degli aeroporti devono avere lunghezza 3 e devono essere letterali"
            else:
                url = 'http://rules:5005/ricevi_tratte_Rules'
                payload = {'userid': user[0], 'origine': origine, 'destinazione': destinazione, 'budget': budget}
                headers = {'Content-Type': 'application/json'}
                response = requests.post(url, json=payload, headers=headers)
                print("response count ",response.json()["count"]) 
                if response.json()["count"]!=-1:
                    if response.json()["count"]==1: #la invia solo è il primo cliente ad averla chiesta
                        print("sto inviando")
                        invia_tratta(origine,destinazione)
                    return "Iscrizione effettuata" 
                else:
                    return "Errore durante l'iscrizione"     
        return "autenticazione fallita, si prega di registrarsi"
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
                url = 'http://rules:5005/ricevi_aeroporti_Rules'
                payload = {'userid': user[0], 'origine': origine, 'budget': budget}
                headers = {'Content-Type': 'application/json'}
                response = requests.post(url, json=payload, headers=headers)
                #print(response.status_code) forse devo controllare lo status_code
                if response.json()["count"]!=-1:
                    if response.json()["count"]==1: #la invia solo se è il primo cliente ad averla chiesta
                        invia_aeroporto(origine)
                    return "Iscrizione effettuata"
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
    user=autentica_client(email) 
    if user != False:
        if len(origine)!=3 or len(destinazione)!=3 or origine.isalpha == False or destinazione.isalpha == False:
            return "i codici degli aeroporti devono avere lunghezza 3 e devono essere letterali"
        else:
            url = 'http://rules:5005/elimina_tratte_Rules'
            payload = {'userid': user, 'origine': origine, 'destinazione': destinazione}
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)
            #print(response.status_code) forse devo controllare lo status_code
            #return response.json()
            if response.json()["count"]!=-1:
                if  response.json()["count"]==0: #la invia per eliminarla solo se è 0 il count di persone iscritte
                    invia_tratta(origine,destinazione)
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
            url = 'http://rules:5005/elimina_aeroporto_Rules'
            payload = {'userid': user, 'origine': origine}
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