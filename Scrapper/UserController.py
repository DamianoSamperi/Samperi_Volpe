import UserInfo.py
import Rules.py

def registra_client():
    #prima controllo se era già registrato
    if UserInfo.control_client(email) == FALSE:
        UserInfo.inserisci_client(nome,cognome,email)
    else:
        print("cliente già registrato")

def inserisci_tratta():
    #in teoria non c'è bisogno di fare il controllo perchè l'ho già autenticato prima
    user=UserInfo.get_id_by_email(email)
    Rules.inserisci_tratta(user,origine,destinazione,budget)

def inserisci_aeroporto():
    #in teoria non c'è bisogno di fare il controllo perchè l'ho già autenticato prima
    user=UserInfo.get_id_by_email(email)
    Rules.inserisci_aeroporto(user,origine,budget)

def autentica_client():
    f=UserInfo.control_client(email)
    if f == TRUE:
        print("ok esisti")
    else:
        print("ti devi registrare")
    #f è TRUE se esiste, FALSE se non esiste
    #autentica il cliente

def trova_email_by_tratta(ori,dest,pr):
    users=Rules.get_users_by_tratta_and_budget(ori,dest,pr)
    return users
    #chiamata da elaboratore per trovare le email dei client interessati a una tratta

def trova_email_by_offerte(ori):
    users=Rules.get_users_by_aeroporto(ori)
    return users
    #chiamata da elaboratore per trovare le email dei client interessati a un offerta

def invia_tratta():
    return
    #invia tratta a controllo tratte

def invia_aeroporto():
    return
    #invia aeroporto a controllo tratte
