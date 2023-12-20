import sqlite3
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

conn = sqlite3.connect('users.db')

# Creazione di un cursore per eseguire le query SQL
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cognome TEXT NOT NULL,
        email TEXT NOT NULL
    )
''')

def inserisci_client(nome,cognome,email):
    cursor.execute('''
    INSERT INTO users (nome, cognome, email)
    VALUES (?, ?, ?)
    ''', (nome, cognome, email))

    conn.commit()

def get_email_by_userid(*ids):
    users=[]
    for id in ids:
        cursor.execute("SELECT email FROM users WHERE id=" +id)
        user = cursor.fetchall()
        users.append(user)
    return users

def control_client(email):
    cursor.execute("SELECT id FROM users WHERE email=" + email)
    result=cursor.fetchall()
    if result != None:
        return result
    else:
        return False

#la chiamo solo se crasha qualcosa
def crash():
    conn.close()

#FLASK----------------------------------------------------------------------------------
@app.route('/controlla_utente', methods=['GET'])
def controlla_utente():
    email = request.args.get('email')
    id=control_client(email)
    result = {'userid': id}
    return jsonify(result)

@app.route('/registra_utente', methods=['POST'])
def inserisci_utente():
    if request.method == 'POST': #forse è request?
        data = request.json
        inserisci_client(data.nome,data.cognome,data.email)
        result = {'message': 'Data received successfully', 'data': data}
        return jsonify(result) 
    
@app.route('/trova_email_by_user_id', methods=['POST'])
def inserisci_utente():
    if request.method == 'POST': #forse è request?
        data = request.json
        data_dict = json.loads(data)
        emails=get_email_by_userid(*data_dict.values())
        return jsonify(emails) 