import sqlite3
from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)

#FORSE IN REALTà SERVE SOLO UN CONN E UN CURSOR, VEDIAMO
#PERCHè UNICO DB MA PIù TABELLE
try:
    conn=sqlite3.connect('voli.db')
    #conn1 = sqlite3.connect('tratte.db')
    #conn2 = sqlite3.connect('aeroporti.db')
    #cursor1 = conn1.cursor()
    #cursor2 = conn2.cursor()
    cursor=conn.cursor()
except sqlite3.Error as e:
    print("Errore durante la connessione al database: {e}")

try:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tratte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            origine TEXT NOT NULL,
            destinazione TEXT NOT NULL,
            budget INTEGER
        )
    ''')
except sqlite3.Error as e:
    print("Errore durante l'esecuzione della query: {e}")

try:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aeroporti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            origine TEXT NOT NULL,
            budget INTEGER
        )
    ''')
except sqlite3.Error as e:
    print("Errore durante l'esecuzione della query: {e}")

def inserisci_tratta(user_id,origine,destinazione,budget):
    try:
        cursor.execute('''
        INSERT INTO tratte (user_id, origine, destinazione, budget)
        VALUES (?, ?, ?, ?)
        ''', (user_id, origine, destinazione, budget))
        conn.commit()
        #ritorna il numero di utenti iscritti a quella tratta
        query="SELECT COUNT(*) FROM tratte WHERE origine= ? AND destinazione= ?"
        cursor.execute(query,(origine, destinazione)) #vedi meglio
        result=cursor.fetchall()
        return result
    except sqlite3.Error as e:
        print("Errore durante l'esecuzione della query: {e}")

def inserisci_aeroporto(user_id,origine,budget):
    try:
        cursor.execute('''
        INSERT INTO aeroporti (user_id, origine, budget)
        VALUES (?, ?, ?, ?)
        ''', (user_id, origine, budget))
        conn.commit()
        #ritorna il numero di utenti iscritti a quell'aeroporto
        query="SELECT COUNT(*) FROM aeroporti WHERE origine= ?"
        cursor.execute(query,(origine,)) #vedi meglio
        result=cursor.fetchall()
        return result
    except sqlite3.Error as e:
        print("Errore durante l'esecuzione della query: {e}")

def get_tratte():
    try:
        cursor.execute(" SELECT * from tratte")
        result=cursor.fetchall()
    except sqlite3.Error as e:
        print("Errore durante l'esecuzione della query: {e}")
    return result

def get_aeroporti():
    try:
        cursor.execute(" SELECT * from aeroporti")
        result=cursor.fetchall()
    except sqlite3.Error as e:
        print("Errore durante l'esecuzione della query: {e}")
    return result 

def get_users_by_tratta_and_budget(origine,destinazione,prezzo):
    try:
        query="SELECT user_id FROM tratte WHERE origine= ? AND destinazione= ? AND budget>= ?"
        cursor.execute(query,(origine, destinazione, prezzo)) #vedi meglio
        users=cursor.fetchall() #insieme di userid interessati in quella tratta
    except sqlite3.Error as e:
        print("Errore durante l'esecuzione della query: {e}")
    url='http://localhost:5000/trova_email_by_user_id'
    result = requests.post(url, jsonify(users)) #credo sia così
    return result

def get_users_by_aeroporto(aeroporto):
    try:
        query=" SELECT user_id FROM aeroporti WHERE origine= ?"
        cursor.execute(query,(aeroporto,)) #vedi meglio
        users=cursor.fetchall() #insieme di userid interessati in quell'aeroporto
    except sqlite3.Error as e:
        print("Errore durante l'esecuzione della query: {e}")
    url='http://localhost:5000/trova_email_by_user_id'
    result = requests.post(url, jsonify(users)) #credo sia così
    return result

def elimina_tratta(user_id,origine,destinazione):
    try:
        query1="DELETE FROM tratte WHERE user_id= ? AND origine= ? AND destinazione= ?"
        cursor.execute(query1,(user_id,origine,destinazione)) #vedi meglio
        conn.commit()
        #ritorna il numero di utenti iscritti a quella tratta
        query2="SELECT COUNT(*) FROM tratte WHERE origine= ? AND destinazione= ?"
        cursor.execute(query2,(origine,destinazione)) #vedi meglio
        result=cursor.fetchall()
        return result
    except sqlite3.Error as e:
        print("Errore durante l'esecuzione della query: {e}")

def elimina_aeroporto(user_id,origine):
    try:
        query1="DELETE FROM aeroporti WHERE user_id= ? AND origine= ?"
        cursor.execute(query1,(user_id,origine)) #vedi meglio
        conn.commit()
        #ritorna il numero di utenti iscritti a quell'aeroporto'
        query2="SELECT COUNT(*) FROM aeroporti WHERE origine= ?"
        cursor.execute(query2,(origine,))
        result=cursor.fetchall()
        return result
    except sqlite3.Error as e:
        print("Errore durante l'esecuzione della query: {e}")

#la chiamo solo se crasha qualcosa 
def crash():
    try:
        #conn1.close()
        #conn2.close()
        conn.close()
    except sqlite3.Error as e:
        print("Errore durante la chiusura della connessione al database: {e}")

#FLASK----------------------------------------------------------------------------------
@app.route('/ricevi_tratte_Rules', methods=['POST'])
def ricevi_tratte():
    if request.method == 'POST': #forse è request?
        data = request.json
        result=inserisci_tratta(data.userid,data.origine,data.destinazione,data.budget)
        return result
  
@app.route('/ricevi_aeroporti_Rules', methods=['POST'])
def ricevi_aeroporti():
    if request.method == 'POST': #forse è request?
        data = request.json
        result=inserisci_aeroporto(data.userid,data.origine,data.budget)
        return result
    
@app.route('/trova_email_by_tratta_rules', methods=['POST'])
def email_by_tratta():
    if request.method == 'POST': #forse è request?
        data = request.json
        result=get_users_by_tratta_and_budget(data.ori,data.dest,data.pr)
        return result
    
@app.route('/trova_email_by_aeroporti_rules', methods=['POST'])
def email_by_aeroporti():
    if request.method == 'POST': #forse è request?
        data = request.json
        result=get_users_by_aeroporto(data.ori)
        return result
    
@app.route('/elimina_tratte_Rules', methods=['POST'])
def ricevi_tratte():
    if request.method == 'POST': #forse è request?
        data = request.json
        result=elimina_tratta(data.userid,data.origine,data.destinazione)
        return result
    
@app.route('/elimina_aeroporto_Rules', methods=['POST'])
def ricevi_tratte():
    if request.method == 'POST': #forse è request?
        data = request.json
        result=elimina_aeroporto(data.userid,data.origine)
        return result

    