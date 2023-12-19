import sqlite3
from flask import Flask, request, jsonify

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

def get_clients():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return users

def control_client(email):
    cursor.execute("SELECT user_id FROM users WHERE email=" + email)
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