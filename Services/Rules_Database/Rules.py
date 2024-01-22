# import sqlite3
import time
from flask import Flask, request
import json
import requests
import mysql.connector
import os

app = Flask(__name__)

# try:
#     conn=sqlite3.connect('rules.db',check_same_thread=False)
#     cursor=conn.cursor()
# except sqlite3.Error as e:
#     print(f"Errore durante la connessione al database: {e}")

#fare creazione delle tabelle a parte
# try:
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS tratte (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER NOT NULL,
#             origine TEXT NOT NULL,
#             destinazione TEXT NOT NULL,
#             budget INTEGER,
#             adulti INTEGER
#         )
#     ''')
# except sqlite3.Error as e:
#     print(f"Errore durante l'esecuzione della query: {e}")

# try:
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS aeroporti (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER NOT NULL,
#             origine TEXT NOT NULL,
#             budget INTEGER
#         )
#     ''')
# except sqlite3.Error as e:
#     print(f"Errore durante l'esecuzione della query: {e}")
while(True):
    try:
        conn = mysql.connector.connect(user='root', password='password', host='mysql', database='rules')
        cursor = conn.cursor()
        break
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
        time.sleep(10)

 
def get_tratte():
    try:
        cursor.execute(" SELECT * from tratte")
        result=cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
    return result

def get_aeroporti():
    try:
        cursor.execute(" SELECT * from aeroporti")
        result=cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
    return result 


def get_users_by_tratta_and_budget(origine,destinazione,prezzo,adulti):
    try:
        query="SELECT user_id FROM tratte WHERE origine= %s AND destinazione= %s AND budget>= %s AND adulti= %s"
        cursor.execute(query,(origine, destinazione, prezzo, adulti))
        users=cursor.fetchall() #insieme di userid interessati in quella tratta
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
    url='http://users-service:5001/trova_email_by_user_id'
    result = requests.post(url, json=json.dumps(users))
    print("result info",result.json())
    return result.json()

def get_users_by_aeroporto(aeroporto,prezzo):
    try:
        query=" SELECT user_id FROM aeroporti WHERE origine= %s AND budget>= %s"
        cursor.execute(query,(aeroporto,prezzo))
        users=cursor.fetchall() #insieme di userid interessati in quell'aeroporto
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
    url='http://users-service:5001/trova_email_by_user_id'
    result = requests.post(url, json=json.dumps(users))
    return result.json()


def inserisci_tratta(user_id,origine,destinazione,budget,adulti):
    try:
        #vedo se l'utente è già iscritto alla tratta
        query="SELECT COUNT(*) FROM tratte WHERE user_id = %s AND origine= %s AND destinazione= %s AND adulti= %s"
        cursor.execute(query,(user_id, origine, destinazione, adulti))
        Count=cursor.fetchone()
        #se non è iscritto lo inserisco, sennò non lo inserisco
        if Count[0]==0:
            query="INSERT INTO tratte (user_id, origine, destinazione, budget, adulti) VALUES(%s, %s, %s, %s, %s)"
            cursor.execute(query, (user_id, origine, destinazione, budget, adulti))
            conn.commit()
        #ritorna il numero di utenti iscritti a quella tratta
        query="SELECT COUNT(*) FROM tratte WHERE origine= %s AND destinazione= %s AND adulti= %s"
        cursor.execute(query,(origine, destinazione, adulti))
        result=cursor.fetchone()
        return result[0]+Count[0]
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
        return -1

def inserisci_aeroporto(user_id,origine,budget):
    try:
        query="SELECT COUNT(*) FROM aeroporti WHERE user_id = %s AND origine= %s"
        #vedo se l'utente è già iscritto a questo aeroporto
        cursor.execute(query,(user_id,origine))
        Count=cursor.fetchone()
        #se non è iscritto lo inserisco
        if Count[0]==0:
            query = "INSERT INTO aeroporti (user_id, origine, budget) VALUES (%s, %s, %s)"
            cursor.execute(query, (user_id, origine, budget))
            conn.commit()
        #ritorna il numero di utenti iscritti a quell'aeroporto
        query="SELECT COUNT(*) FROM aeroporti WHERE origine= %s"
        cursor.execute(query,(origine,))
        result=cursor.fetchone()
        return result[0]+Count[0]
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
        return -1


def elimina_tratta(user_id,origine,destinazione,adulti):
    try:
        query1="DELETE FROM tratte WHERE user_id= %s AND origine= %s AND destinazione= %s AND adulti= %s"
        cursor.execute(query1,(user_id,origine,destinazione,adulti))
        trovati=cursor.rowcount #numero di righe eliminate
        conn.commit()
        if trovati==0:
            return [-1]
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query DELETE: {e}")
    try:
        #ritorna il numero di utenti iscritti a quella tratta
        query2="SELECT COUNT(*) FROM tratte WHERE origine= %s AND destinazione= %s AND adulti= %s"
        cursor.execute(query2,(origine,destinazione,adulti))
        result=cursor.fetchone()
        return result
        #return [trovati,result]
        #return json.dumps({"trovati": trovati, "count": result[0]})
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query SELECT: {e}")

def elimina_aeroporto(user_id,origine):
    try:
        query1="DELETE FROM aeroporti WHERE user_id= %s AND origine= %s"
        cursor.execute(query1,(user_id,origine))
        trovati=cursor.rowcount #numero di righe eliminate
        #print(trovati)
        conn.commit()
        if trovati==0:
            return [-1]
        #ritorna il numero di utenti iscritti a quell'aeroporto'
        query2="SELECT COUNT(*) FROM aeroporti WHERE origine= %s"
        cursor.execute(query2,(origine,))
        result=cursor.fetchone()
        return result
        #return [trovati,result]
        #return json.dumps({"trovati": trovati, "count": result[0]})
    except mysql.connector.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")

#la chiamo solo se crasha qualcosa 
def crash():
    try:
        #conn1.close()
        #conn2.close()
        conn.close()
    except mysql.connector.Error as e:
        print(f"Errore durante la chiusura della connessione al database: {e}")

#FLASK----------------------------------------------------------------------------------
@app.route('/ricevi_tratte_Rules', methods=['POST'])
def ricevi_tratte():
    if request.method == 'POST': 
        data = request.json 
        result=inserisci_tratta(data["userid"],data["origine"],data["destinazione"],data["budget"],data["adulti"])
        Count = {"count":result}
        return Count
  
@app.route('/ricevi_aeroporti_Rules', methods=['POST'])
def ricevi_aeroporti():
    if request.method == 'POST': 
        data = request.json
        result=inserisci_aeroporto(data["userid"],data["origine"],data["budget"])
        Count = {"count":result}
        return Count
    
@app.route('/trova_email_by_tratta_rules', methods=['POST'])
def email_by_tratta():
    if request.method == 'POST': 
        data = request.json
        print("data rules",data)
        result=get_users_by_tratta_and_budget(data['ori'],data['dest'],data['pr'],data['adulti'])
        print("result",result)
        return result
    
@app.route('/trova_email_by_aeroporti_rules', methods=['POST'])
def email_by_aeroporti():
    if request.method == 'POST': 
        data = request.json
        result=get_users_by_aeroporto(data['ori'],data['pr'])
        return result
    
@app.route('/elimina_tratte_Rules', methods=['POST'])
def elimina_tratte():
    if request.method == 'POST': 
        data = request.json
        result=elimina_tratta(data['userid'],data['origine'],data['destinazione'],data['adulti'])
        Count = {"count":result[0]}
        return Count
    
@app.route('/elimina_aeroporto_Rules', methods=['POST'])
def elimina_aeroporti():
    if request.method == 'POST': 
        data = request.json
        result=elimina_aeroporto(data['userid'],data['origine'])
        Count = {"count":result[0]}
        return Count

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5005, debug=True, threaded=True)