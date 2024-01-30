import os
import socket
import json
import time
import mysql.connector
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

while(True):
    try:
        conn = mysql.connector.connect(user='root', password='password', host='mysql', database='controllertratte')
        cursor = conn.cursor()
        break
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
        time.sleep(10)

    
def leggi_database():
    try:
        cursor.execute("SELECT * FROM tratte_salvate")
        risultati = cursor.fetchall()
        cursor.execute("SELECT * FROM aeroporti_salvati")
        risultati2 = cursor.fetchall()

    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")

    tratte = []
    aeroporti = []

    for tupla in risultati:
        tratte.append(tupla)
    for tupla in risultati2:
        aeroporti.append(tupla)

    return tratte,aeroporti

def leggi_database_tratte():
    try:
        cursor.execute("SELECT * FROM tratte_salvate")

        risultati = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
        return "error"

    tratte = []

    for tupla in risultati:
        tratte.append({"origine": tupla[1] , "destinazione" : tupla[2], "adulti": tupla[3]})

    return tratte

def leggi_database_aeroporti():
    try:
        cursor.execute("SELECT * FROM aeroporti_salvati")

        risultati = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
        return "error"

    aeroporti = []

    for tupla in risultati:
        aeroporti.append({"origine": tupla[1] })

    return aeroporti

def scrivi_database_tratte(data):
    try:
        query = "SELECT COUNT(*) FROM tratte_salvate WHERE origine = %s AND destinazione = %s AND adulti= %s"
    
        cursor.execute(query, (data['origine'], data['destinazione'], data['adulti']))
        count = cursor.fetchone()
        
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
        raise "errore connesione"
    if count[0]==0:
        try:
            query = "INSERT INTO tratte_salvate ( origine, destinazione, adulti) VALUES (%s, %s, %s)"
            cursor.execute(query, (data['origine'], data['destinazione'], data['adulti']))
            conn.commit()
            return 'ok'
        except mysql.connector.Error as e:
            print(f"Errore durante l'esecuzione della query: {e}")
            raise "insert error"
    else:
        try:
            query = "DELETE FROM tratte_salvate WHERE origine = %s AND destinazione = %s AND adulti= %s"
            cursor.execute(query, (data['origine'], data['destinazione'], data['adulti']))
            conn.commit()
            return 'ok'
        except mysql.connector.Error as e:
            print(f"Errore durante l'esecuzione della query: {e}")
            raise "delete error"


def scrivi_database_aeroporti(data):
    try:
        query = "SELECT COUNT(*) FROM aeroporti_salvati WHERE origine = %s" 
    
        cursor.execute(query, (data['aeroporto'],)) 
        count = cursor.fetchone()

        conn.commit()
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
        raise "errore connesione"
    if count[0] == 0:
        try:
            query = "INSERT INTO aeroporti_salvati ( origine) VALUES (%s )"
            cursor.execute(query, (data['aeroporto'],))
            conn.commit()
            return 'ok'
        except mysql.connector.Error as e:
            print(f"Errore durante l'esecuzione della query: {e}")
            raise "insert error"
    else:
        try:
            query = "DELETE FROM aeroporti_salvati WHERE origine = %s"
            cursor.execute(query, (data['aeroporto'],))
            conn.commit()
            return 'ok'
        except mysql.connector.Error as e:
            print(f"Errore durante l'esecuzione della query: {e}")
            raise "delete error"

@app.route('/invio_Scraper', methods=['POST']) 
def comunicazione_Scraper():
    richiesta= request.json
    if richiesta['request']=='tratta':
        tratte= leggi_database_tratte()
        return tratte
    elif richiesta['request'] == 'aeroporto':
        aeroporti=leggi_database_aeroporti()
        return aeroporti
    return "error"

@app.route('/ricevi_tratte_usercontroller', methods=['POST']) 
def comunicazioneUser_tratte():
    try:
        tratta= request.json
        response = scrivi_database_tratte(tratta)
        return response
    except Exception as e:
        if e == "delete error":
            return jsonify(error="delete error"), 500
        elif e == "insert error":
            return jsonify(error="insert error"), 500
        else:
            return jsonify(error="connession error"), 500
        
@app.route('/ricevi_aeroporto_usercontroller', methods=['POST']) 
def comunicazioneUser_aeroporto():
    aeroporto = request.json
    try:
        response = scrivi_database_aeroporti(aeroporto)
        return response
    except Exception as e:
        if e == "delete error":
            return jsonify(error="delete error"), 500
        elif e == "insert error":
            return jsonify(error="insert error"), 500
        else:
            return jsonify(error="connession error"), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5002, debug=True, threaded=True)
