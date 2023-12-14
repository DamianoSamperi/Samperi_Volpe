import UserInfo
import Rules

def registra_client():
    UserInfo.inserisci_client(nome,cognome,email)

#forse ha più senso fare un unico metodo e in base al tipo di richiesta passata
#(tratta o aeroporto), allora chiama la funzione giusta del microservizio Rules
def inserisci_tratta():
    user=UserInfo.get_id_by_email(email)
    Rules.inserisci_tratta(user,origine,destinazione,budget)

def inserisci_aeroporto():
    user=UserInfo.get_id_by_email(email)
    Rules.inserisci_aeroporto(user,origine,budget)

def autentica_client():
    f=UserInfo.control_client(email)
    #f è TRUE se esiste, FALSE se non esiste
    #autentica il cliente

def trova_email(rules):
    return
    #chiamata da elaboratore per trovare le email dei client interessati

def invia_tratta():
    return
    #invia tratta a kafka

def invia_aeroporto():
    return
    #invia aeroporto a kafka
