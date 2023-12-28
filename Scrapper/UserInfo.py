import sqlite3
from flask import Flask, request, jsonify
import json

app = Flask(__name__)
try:
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
except sqlite3.Error as e:
    print("Errore durante la connessione al database: {e}")

try:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cognome TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
except sqlite3.Error as e:
    print("Errore durante l'esecuzione della query: {e}")

def inserisci_client(nome,cognome,email):
    try:
        cursor.execute('''
        INSERT INTO users (nome, cognome, email)
        VALUES (?, ?, ?)
        ''', (nome, cognome, email))
        conn.commit()
    except sqlite3.Error as e:
        print("Errore durante l'esecuzione della query: {e}")

def get_email_by_userid(*ids):
    users=[]
    for id in ids:
        try:
            query="SELECT email FROM users WHERE id= ?"
            cursor.execute(query, (id[0],)) #TO_DO andrebbero messe delle stampe per vedere che stiamo facendo
            user = cursor.fetchall()
            users.append(user[0])
        except sqlite3.Error as e:
            print("Errore durante l'esecuzione della query: {e}")
    return users

def control_client(email):
    try:
        query="SELECT id FROM users WHERE email= ?"
        cursor.execute(query,(email,)) #TO_DO andrebbero messe delle stampe per vedere che stiamo facendo
        result=cursor.fetchall()
    except sqlite3.Error as e:
        print("Errore durante l'esecuzione della query: {e}")
    if result != None:
        return result
    else:
        return False

#la chiamo solo se crasha qualcosa
def crash():
    try:
        conn.close()
    except sqlite3.Error as e:
        print("Errore durante la chiusura della connessione al database: {e}")

#FLASK----------------------------------------------------------------------------------
@app.route('/controlla_utente', methods=['GET'])
def controlla_utente():
    email = request.args.get('email')
    id=control_client(email)
    result = {'userid': id}
    return jsonify(result)

@app.route('/registra_utente', methods=['POST'])
def inserisci_utente():
    if request.method == 'POST': 
        #data = request.json
        data=json.loads(request.json)
        inserisci_client(data["nome"],data["cognome"],data["email"]) #vedi se funziona
        result = {'message': 'Data received successfully', 'data': data}
        return jsonify(result) 
    
@app.route('/trova_email_by_user_id', methods=['POST'])
def inserisci_utente():
    if request.method == 'POST': 
        data = request.json
        data_dict = json.loads(data)
        emails=get_email_by_userid(*data_dict)
        return jsonify(emails) 