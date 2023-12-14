import UserInfo
import Rules

#non so se conviene di fare il main, intanto lo faccio così
def main():
    while True:
        print("ciao utente")
 
        utente = []
        stringa = input("Inserisci il nome: ")
        utente.append(stringa)
        stringa = input("Inserisci il cognome: ")
        utente.append(stringa)
        stringa = input("Inserisci email: ")
        utente.append(stringa)

        print("i tuoi dati sono:", utente)
        registra_client(utente)



if __name__== '__main__':
    main()
#fine forse

def registra_client(utente):
    #prima controllo se era già registrato
    if UserInfo.control_client(utente[2]) == False:
        UserInfo.inserisci_client(utente[0],utente[1],utente[2])
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
    if f == True:
        print("ok esisti")
    else:
        print("ti devi registrare")
    #f è TRUE se esiste, FALSE se non esiste
    #autentica il cliente

#def trova_email(msg)
        #potremmo fare un if qui dentro e in base al tipo di msg che ha trovato, chiama
        #by tratta o by offerte

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
