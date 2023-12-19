import UserInfo
import Rules
from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)  

#TO_DO aggiungere comunicazione tra microservizi dapertutto
    
def registra_client(utente):
    #prima controllo se era già registrato
    if UserInfo.control_client(utente[2]) == False:
        UserInfo.inserisci_client(utente[0],utente[1],utente[2])
    else:
        print("cliente già registrato")

def inserisci_tratta(email, origine, destinazione, budget):
    user=autentica_client(email)

    #Rules.inserisci_tratta(user,origine,destinazione,budget)
    url = 'http://localhost:5000/ricevi_tratte_Rules'
    payload = {'userid': user, 'origine': origine, 'destinazione': destinazione, 'budget': budget}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    # Stampa la risposta ricevuta dal servizio
    print(response.status_code)
    print(response.json())

    invia_tratta(origine,destinazione)

def inserisci_aeroporto(email,origine,budget):
    user=autentica_client(email)

    #Rules.inserisci_aeroporto(user,origine,budget)
    url = 'http://localhost:5000/ricevi_aeroporti_Rules'
    payload = {'userid': user, 'origine': origine, 'budget': budget}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    # Stampa la risposta ricevuta dal servizio
    print(response.status_code)
    print(response.json())

    invia_aeroporto(origine)

def autentica_client(email):
    url = 'http://localhost:5000/controlla_utente'
    params = {'email': email}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            user=response.json.userid
            if user==False:
                print("non sei registrato")
                #TO-DO DOVREBBE USCIRE DA QUI E DA TUTTE LE FUNZIONI
            else:
                print("ok esisti")
                return user
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

#def trova_email(msg)
        #potremmo fare un if qui dentro e in base al tipo di msg che ha trovato, chiama
        #by tratta o by offerte

def trova_email_by_tratta(ori,dest,pr):
    users=Rules.get_users_by_tratta_and_budget(ori,dest,pr)
    return users
    #chiamata da elaboratore per trovare le email dei client interessati a una tratta
    #devo fare una GET

def trova_email_by_offerte(ori):
    users=Rules.get_users_by_aeroporto(ori)
    return users
    #chiamata da elaboratore per trovare le email dei client interessati a un offerta
    #devo fare una GET

#TO-DO vedi meglio
def invia_tratta(origine, destinazione):
    # URL del servizio Flask
    url = 'http://localhost:5000/ricevi_tratte_usercontroller'

    # Dati da inviare con la richiesta POST
    payload = {'origine': origine, 'destinazione': destinazione}

    # Imposta l'intestazione della richiesta per indicare che stai inviando dati JSON
    headers = {'Content-Type': 'application/json'}

    # Invia la richiesta POST al servizio Flask
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    # Stampa la risposta ricevuta dal servizio
    print(response.status_code)
    print(response.json())

#TO-DO vedi meglio
def invia_aeroporto(aeroporto):
    # URL del servizio Flask
    url = 'http://localhost:5000/ricevi_aeroporto_usercontroller'

    # Dati da inviare con la richiesta POST
    payload = {'aeroporto': aeroporto}

    # Imposta l'intestazione della richiesta per indicare che stai inviando dati JSON
    headers = {'Content-Type': 'application/json'}

    # Invia la richiesta POST al servizio Flask
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    # Stampa la risposta ricevuta dal servizio
    print(response.status_code)
    print(response.json())

