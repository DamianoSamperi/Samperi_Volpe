import UserInfo
import Rules
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

#non so se conviene di fare il main, intanto lo faccio così
#TO_DO non è il cliente questo, non è nemmeno neccesario averne uno
'''def main():
    scelta=None
    while scelta != 0:
        stampa_menu()
        try:
            scelta = int(input("Inserisci il numero corrispondente all'opzione desiderata: "))
        except ValueError:
            print("Inserisci un numero valido.")
            continue

        if scelta == 1:
            registrazione()
        elif scelta == 2:
            accesso()
        elif scelta == 3:
            tratta()
        elif scelta == 4:
            aeroporto()
        elif scelta == 0:
            print("Uscita dal programma.")
            #chiudo la sessione utente
        else:
            print("inserisci una scelta valida")
            main() #vedi se si fa così

if __name__== '__main__':
    main()
#fine forse
    
def stampa_menu():
    print("ciao utente")
    print("\nMenu:")
    print("1. registrati")
    print("2. accedi")
    print("3. inserisci una nuova tratta")
    print("4. inserisci un nuovo aeroporto interessato")
    print("0. Esci")

def registrazione():
    utente = []
    stringa = input("Inserisci il nome: ")
    utente.append(stringa)
    stringa = input("Inserisci il cognome: ")
    utente.append(stringa)
    stringa = input("Inserisci email: ")
    utente.append(stringa)
    print("i tuoi dati sono:", utente)
    registra_client(utente)

def accesso():
    email=input("inserisci la tua email")
    autentica_client(email)

def tratta():
    #facciamo un controllo se ancora non aveva fatto l'accesso 
    #dobbiamo fare una sorta di sessione
    email=input("inserisci la tua email")
    autentica_client(email)
    origine=input("inserisci aeroporto origine: ")
    destinazione=input("inserisci aeroporto destinazione: ")
    budget=int(input("inserisci il tuo budget: "))
    inserisci_tratta(email,origine,destinazione,budget)

def aeroporto():
    #facciamo un controllo se ancora non aveva fatto l'accesso 
    #dobbiamo fare una sorta di sessione
    email=input("inserisci la tua email")
    autentica_client(email)
    origine=input("inserisci aeroporto origine: ")
    budget=int(input("inserisci il tuo budget, 9999 se non hai un budget: "))
    inserisci_aeroporto(email,origine,budget)'''   

#TO_DO aggiungere comunicazione tra microservizi dapertutto
    
def registra_client(utente):
    #prima controllo se era già registrato
    if UserInfo.control_client(utente[2]) == False:
        UserInfo.inserisci_client(utente[0],utente[1],utente[2])
    else:
        print("cliente già registrato")

def inserisci_tratta(email, origine, destinazione, budget):
    #in teoria non c'è bisogno di fare il controllo perchè l'ho già autenticato prima
    user=UserInfo.control_client(email)
    #Rules.inserisci_tratta(user,origine,destinazione,budget)

    url = 'http://localhost:5000/ricevi_tratte_Rules'
    payload = {'userid': user, 'origine': origine, 'destinazione': destinazione, 'budget': budget}
    headers = {'Content-Type': 'application/json'}
    response = request.post(url, data=json.dumps(payload), headers=headers)
    # Stampa la risposta ricevuta dal servizio
    print(response.status_code)
    print(response.json())

    invia_tratta(origine,destinazione)

def inserisci_aeroporto(email,origine,budget):
    #in teoria non c'è bisogno di fare il controllo perchè l'ho già autenticato prima
    user=UserInfo.control_client(email)
    #Rules.inserisci_aeroporto(user,origine,budget)

    url = 'http://localhost:5000/ricevi_aeroporti_Rules'
    payload = {'userid': user, 'origine': origine, 'budget': budget}
    headers = {'Content-Type': 'application/json'}
    response = request.post(url, data=json.dumps(payload), headers=headers)
    # Stampa la risposta ricevuta dal servizio
    print(response.status_code)
    print(response.json())

    invia_aeroporto(origine)

def autentica_client(email):
    f=UserInfo.control_client(email)
    if f == True:
        print("ok esisti")
    else:
        print("ti devi registrare")
        #main() #vedi se si fa così

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
    response = request.post(url, data=json.dumps(payload), headers=headers)

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
    response = request.post(url, data=json.dumps(payload), headers=headers)

    # Stampa la risposta ricevuta dal servizio
    print(response.status_code)
    print(response.json())


#TO-DO PROVA FLASK--------------------------------------------------------

'''app=Flask(__name__)

#@app.route('/inviodati_controllotratte', methods=['POST']) 
#def comunicazionepost():
 #   tratte = leggi_database()
  #  response = requests.post('http://localhost:5000/recuperodati_scraper', tratte=tratte)
   # return response.text 

# URL del servizio Flask
url = 'http://localhost:5000/api/tratte'

# Dati da inviare con la richiesta POST
payload = {'nome': 'John', 'cognome': 'Doe', 'eta': 30}

# Imposta l'intestazione della richiesta per indicare che stai inviando dati JSON
headers = {'Content-Type': 'application/json'}

# Invia la richiesta POST al servizio Flask
response = requests.post(url, data=json.dumps(payload), headers=headers)

# Stampa la risposta ricevuta dal servizio
print(response.status_code)
print(response.json())'''

