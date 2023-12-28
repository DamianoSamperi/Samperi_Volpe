from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)  


# def registra_client(nome,cognome,email):
#     #prima controllo se era già registrato
#     if autentica_client(email) == False:
#         url = 'http://localhost:5000/registra_utente'
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
#         url = 'http://localhost:5000/ricevi_tratte_Rules'
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
#         url = 'http://localhost:5000/ricevi_aeroporti_Rules'
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
#         url = 'http://localhost:5000/elimina_tratte_Rules'
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
#         url = 'http://localhost:5000/elimina_aeroporto_Rules'
#         payload = {'userid': user, 'origine': origine}
#         headers = {'Content-Type': 'application/json'}
#         response = requests.post(url, json=payload, headers=headers)
#         #print(response.status_code) forse devo controllare lo status_code
#         if response==0: #la invia per eliminarla solo se è 0 il count di persone iscritte
#             invia_aeroporto(origine)       

def autentica_client(email):
    url = 'http://localhost:5000/controlla_utente'
    params = {'email': email}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            user=response.json['userid']
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
    #users=Rules.get_users_by_tratta_and_budget(ori,dest,pr)
    url='http://localhost:5000/trova_email_by_tratta_rules'
    result = requests.post(url, json={'ori':ori, 'dest': dest,'pr': pr})
    return result

def trova_email_by_offerte(ori):
    #users=Rules.get_users_by_aeroporto(ori)
    url='http://localhost:5000/trova_email_by_aeroporti_rules'
    result = requests.post(url, json={'ori':ori,})
    return result

#TO-DO vedi meglio
def invia_tratta(origine, destinazione):
    url = 'http://localhost:5002/ricevi_tratte_usercontroller'
    payload = {'origine': origine, 'destinazione': destinazione}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    # Stampa la risposta ricevuta dal servizio
    print(response.status_code)
    print(response.json())

#TO-DO vedi meglio
def invia_aeroporto(aeroporto):
    url = 'http://localhost:5002/ricevi_aeroporto_usercontroller'
    payload = {'aeroporto': aeroporto}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    # Stampa la risposta ricevuta dal servizio
    print(response.status_code)
    print(response.json())

#FLASK----------------------------------------------------------------------------------
@app.route('/trova_email_by_tratta', methods=['POST'])
def trova_email_tratta():
    if request.method == 'POST':
        data = request.json 
        result=trova_email_by_tratta(data["ori"],data["dest"],data["pr"])
        return result
    
@app.route('/trova_email_by_offerte', methods=['POST'])
def trova_email_offerte():
    if request.method == 'POST':
        data = request.json
        result=trova_email_by_offerte(data["ori"])
        return result
    
@app.route('/registrazione', methods=['POST'])
def registra_client():
    data= request.json
    #prima controllo se era già registrato
    if autentica_client(data["email"]) == False:
        url = 'http://localhost:5001/registra_utente'
        payload = {'email': data["email"], 'nome': data["nome"], 'cognome': data["cognome"]}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        # Stampa la risposta ricevuta dal servizio
        print(response.status_code)
        return response["message"]
    else:
        return "cliente già registrato"


@app.route('/Insert_tratta', methods=['POST'])
def inserisci_tratta():
    data= request.json
    email = data["emai"]
    origine = data["origine"]
    destinazione = data["destinazione"]
    budget = data["budget"]
    user=autentica_client(email) 
    if user != False:
        #Rules.inserisci_tratta(user,origine,destinazione,budget)
        url = 'http://localhost:5005/ricevi_tratte_Rules'
        payload = {'userid': user, 'origine': origine, 'destinazione': destinazione, 'budget': budget}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        #print(response.status_code) forse devo controllare lo status_code
        if response==1: #la invia solo è il primo cliente ad averla chiesta
            invia_tratta(origine,destinazione)

@app.route('/Insert_aeroporto', methods=['POST'])
def inserisci_aeroporto():
    data= request.json
    email = data["emai"]
    origine = data["origine"]
    budget = data["budget"]
    user=autentica_client(email)
    if user != False:
        #Rules.inserisci_aeroporto(user,origine,budget)
        url = 'http://localhost:5005/ricevi_aeroporti_Rules'
        payload = {'userid': user, 'origine': origine, 'budget': budget}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        #print(response.status_code) forse devo controllare lo status_code
        if response==1: #la invia solo se è il primo cliente ad averla chiesta
            invia_aeroporto(origine)


#TO_DO Elena bisogna fare la disiscrizione o come nuova funziona oppure nelle funzione inserisce puoi controllare se gia inserito e in quel caso cancelli dal database e invi al controller solo se non ci sono utenti per quella tratta-aeroporto
@app.route('/Disiscrizione_tratta', methods=['POST'])
def disiscrizione_tratta():
    data= request.json
    email = data["emai"]
    origine = data["origine"]
    destinazione = data["destinazione"]
    user=autentica_client(email) 
    if user != False:
        #Rules.inserisci_tratta(user,origine,destinazione,budget)
        url = 'http://localhost:5005/elimina_tratte_Rules'
        payload = {'userid': user, 'origine': origine, 'destinazione': destinazione}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        #print(response.status_code) forse devo controllare lo status_code
        if response==0: #la invia per eliminarla solo se è 0 il count di persone iscritte
            invia_tratta(origine,destinazione)

@app.route('/Disiscrizione_aeroporto', methods=['POST'])
def disiscrizione_aeroporto():  
    data= request.json
    email = data["emai"]
    origine = data["origine"]
    user=autentica_client(email) 
    if user != False:
        #Rules.inserisci_tratta(user,origine,destinazione,budget)
        url = 'http://localhost:5005/elimina_aeroporto_Rules'
        payload = {'userid': user, 'origine': origine}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        #print(response.status_code) forse devo controllare lo status_code
        if response==0: #la invia per eliminarla solo se è 0 il count di persone iscritte
            invia_aeroporto(origine)       




if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000, debug=True, threaded=True)