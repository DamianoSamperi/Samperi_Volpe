from msilib import Control
from amadeus import Client, ResponseError
import Controller_tratte
amadeus = Client(
    client_id='mO1GSbwraiZUlQ84AJWQPE6GkxINddt1',
    client_secret='ungA0GVVriDUeztB'
)
trattegestite = 1 #numero di tratte da cercare, potremmo inserirlo insieme al file dei parametri e me li faccio passare
# tratte = Controller_tratte.leggi_file()  caso get method
# trattegestite = len(tratte)
def inviotratta(data):
    print(response)

def controllo_tratta(OC,DC,DD,A):
    try:
        controllo = amadeus.shopping.flight_offers_search.get(originLocationCode=OC, destinationLocationCode=DC, departureDate=DD, adults=A) #se devo mandare un json con i parametri devo usare il post method
        data=f"{OC} {DC} {DD} {A}"
        Controller_tratte.scrivi_file(data)
    except ResponseError as error:
         raise error

while True:
    # json_string = '{ "currencyCode": "ZAR", "originDestinations": [ { "id": "1", "originLocationCode": "JNB", ' \
    #           '"destinationLocationCode": "CPT", "departureDateTimeRange": { "date": "2022-07-01", "time": "00:00:00" ' \
    #           '} }, { "id": "2", "originLocationCode": "CPT", "destinationLocationCode": "JNB", ' \
    #           '"departureDateTimeRange": { "date": "2022-07-29", "time": "00:00:00" } } ], "travelers": [ { "id": ' \
    #           '"1", "travelerType": "ADULT" }, { "id": "2", "travelerType": "ADULT" }, { "id": "3", "travelerType": ' \
    #           '"HELD_INFANT", "associatedAdultId": "1" } ], "sources": [ "GDS" ], "searchCriteria": { ' \
    #           '"excludeAllotments": true, "addOneWayOffers": false, "maxFlightOffers": 10, ' \
    #           '"allowAlternativeFareOptions": true, "oneFlightOfferPerDay": true, "additionalInformation": { ' \
    #           '"chargeableCheckedBags": true, "brandedFares": true, "fareRules": false }, "pricingOptions": { ' \
    #           '"includedCheckedBagsOnly": false }, "flightFilters": { "crossBorderAllowed": true, ' \
    #           '"moreOvernightsAllowed": true, "returnToDepartureAirport": true, "railSegmentAllowed": true, ' \
    #           '"busSegmentAllowed": true, "carrierRestrictions": { "blacklistedInEUAllowed": true, ' \
    #           '"includedCarrierCodes": [ "FA" ] }, "cabinRestrictions": [ { "cabin": "ECONOMY", "coverage": ' \
    #           '"MOST_SEGMENTS", "originDestinationIds": [ "2" ] }, { "cabin": "ECONOMY", "coverage": "MOST_SEGMENTS", ' \
    #           '"originDestinationIds": [ "1" ] } ], "connectionRestriction": { "airportChangeAllowed": true, ' \
    #           '"technicalStopsAllowed": true } } } }'
    #body = json.loads(json_string)   nel caso metodo get non ho bisogno del json però posso farmi passare meno parametri dall'utente però è pure un casino fare il json
    for i in range (1,trattegestite):
        try:
            # response = amadeus.shopping.flight_offers_search.get(originLocationCode='SYD', destinationLocationCode='BKK', departureDate='2023-12-08', adults=1) se devo mandare un json con i parametri devo usare il post method
            # response = amadeus.shopping.flight_offers_search.post(body) nel caso post method
            # biaogna fare una response in cui tutti i paramentri variano al variare di i, quindi magare un microservizio che scrive e legge un file e mi invia un array di stringhe , 
            # print(response.data)
            inviotratta(response) #funzione che permette di inviare al topic kafka la tratta ottenuta
        except ResponseError as error:
            raise error

