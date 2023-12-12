import socket
import json

#questo se vogliamo utilizzare un file
def leggi_file():
    tratte = []
    with open("tratte.txt", 'r') as file:
        for riga in file:
            # tratte.append(estrai_valori("originLocationCode=","destinationLocationCode=",riga))
            # tratte.append(estrai_valori("destinationLocationCode=","departureDate=",riga))
            # tratte.append(estrai_valori("departureDate=","adults=",riga))
            # tratte.append(estrai_valori("adults=","",riga))
            tratte.append(riga.split())         
    return tratte
def estrai_valori(parola_inizio, parola_fine,riga):
    # matrice = []
    # with open("tratte.txt", 'r') as file:
    #     for riga in file:
            parole = riga.split()
            print(parole)
            try:
                indice_inizio = parole.index(parola_inizio) + 1
                indice_fine = parole.index(parola_fine)
            except ValueError as error:
                # continue
                raise error
            valori = parole[indice_inizio:indice_fine]
            return valori

def scrivi_file(data):
    with open("tratte.txt", 'a') as file:
        file.write(data)
#questo se utilizziamo il database Rules
def leggi_database():
    #conn = connessione a database

    # Crea un cursore
    cur = conn.cursor()

    # Esegui una query SQL
    cur.execute("SELECT * FROM tabella_tratte")

    # Ottieni i risultati
    risultati = cur.fetchall()

    # Chiudi la connessione
    conn.close()

    # Inizializza un array vuoto
    tratte = []

    # Itera sui risultati e aggiungi ogni tupla all'array come stringa
    for tupla in risultati:
        tratte.append(tupla)

    # Stampa l'array di stringhe
    return tratte 
def scrivi_database(data):
    #conn = connessione al database

    # Crea un cursore
    cur = conn.cursor()

    # Prepara la query SQL
    query = "INSERT INTO mia_tabella (colonna1, colonna2) VALUES (?, ?, ?, ?, ?)"

    # Esegui la query SQL con i valori passati come parametri
    cur.execute(query, (data[0], data[1], data[2], data[3], data[4]))

    # Esegui il commit delle modifiche
    conn.commit()

    # Chiudi la connessione
    conn.close()

def comunicazionesocket():
    # Crea un socket TCP/IP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Associa il socket a una porta
    server_address = ('localhost', 12345)
    sock.bind(server_address)

    # Ascolta le connessioni in arrivo
    sock.listen(1)

    while True:
        # Attende una connessione
        print('In attesa di una connessione...')
        connection, client_address = sock.accept()

        try:
            print('Connessione da', client_address)

            # Riceve i dati in piccoli segmenti
            # data = connection.recv(16)
            # print('Ricevuto {!r}'.format(data))

            # Invia i dati
            # if data:
            print('Invio del vettore al client')
            vector = leggi_database()
            connection.sendall(vector.encode('utf-8'))

        finally:
            # Pulisce la connessione
            connection.close() 
     