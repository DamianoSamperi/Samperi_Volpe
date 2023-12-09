
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
        
# with open("tratte.txt", 'w+') as file:
#         file.write("prova: 2 funzione")
print(leggi_file())