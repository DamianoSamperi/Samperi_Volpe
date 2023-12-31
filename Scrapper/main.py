from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__) 

def stampa_menu():
    print("ciao utente")
    print("\nMenu:")
    print("1. registrati")
    print("2. inserisci una nuova tratta")
    print("3. inserisci un nuovo aeroporto interessato")
    print("4. disiscriviti da una tratta")
    print("4. disiscriviti da un aeroporto")
    print("0. Esci\n")

def registrazione():
    nome = input("\nInserisci il nome: ")
    cognome = input("Inserisci il cognome: ")
    email = input("Inserisci email: ")
    url='http://localhost:5000/registrazione'
    result = requests.post(url, json={'email':email, 'nome': nome,'cognome': cognome})
    print(result.status_code)
    print(result.text)

def tratta():
    email=input("\ninserisci la tua email")
    origine=input("inserisci aeroporto origine: ")
    destinazione=input("inserisci aeroporto destinazione: ")
    try:
        budget=int(input("inserisci il tuo budget: "))
    except ValueError:
            print("Inserisci un numero valido.")
            main()
    url='http://localhost:5000/Insert_tratta'
    result = requests.post(url, json={'email':email, 'origine': origine,'destinazione': destinazione, 'budget': budget})
    print(result.status_code)
    print (result.text)

def aeroporto():
    email=input("\ninserisci la tua email")
    origine=input("inserisci aeroporto origine: ")
    try:
        budget=int(input("inserisci il tuo budget: "))
    except ValueError:
            print("Inserisci un numero valido.")
            main()
    url='http://localhost:5000/Insert_aeroporto'
    result = requests.post(url, json={'email':email, 'origine': origine, 'budget': budget})
    print(result.status_code)
    print(result.text)

def disiscrivi_tratta():
    email=input("\ninserisci la tua email")
    origine=input("inserisci aeroporto origine: ")
    destinazione=input("inserisci aeroporto destinazione: ")
    url='http://localhost:5000/Disiscrizione_tratta'
    result = requests.post(url, json={'email':email, 'origine': origine,'destinazione': destinazione})
    print(result.status_code)
    print(result.text)

def disiscrivi_aeroporto():
    email=input("\ninserisci la tua email")
    origine=input("inserisci aeroporto origine: ")
    url='http://localhost:5000/Disiscrizione_aeroporto'
    result = requests.post(url, json={'email':email, 'origine': origine})
    print(result.status_code)
    print(result.text)

#TO-DO devo fare app run di flask o va bene così?1
def main():
    while True:
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
                tratta()
            elif scelta == 3:
                aeroporto()
            elif scelta == 4:
                disiscrivi_tratta()
            elif scelta == 5:
                disiscrivi_aeroporto()
            elif scelta == 0:
                print("Uscita dal programma.")
            else:
                print("inserisci una scelta valida")
                continue #vedi se si fa così

if __name__== '__main__':
    main()