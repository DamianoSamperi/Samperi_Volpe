import sqlite3
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

try:
    conn = sqlite3.connect('users.db',check_same_thread=False)
    cursor = conn.cursor()
except sqlite3.Error as e:
    print(f"Errore durante la connessione al database: {e}")

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
    print(f"Errore durante l'esecuzione della query: {e}")



def inserisci_client(nome,cognome,email):
    try:
        cursor.execute('''
        INSERT INTO users (nome, cognome, email)
        VALUES (?, ?, ?)
        ''', (nome, cognome, email))
        conn.commit()
        return 'ok'
    except sqlite3.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
        return e

def get_email_by_userid(*ids):
    users=[]      
    for id in ids:           
        try:
            query="SELECT email FROM users WHERE id= ?"
            cursor.execute(query, (id[0],)) #TO_DO andrebbero messe delle stampe per vedere che stiamo facendo
            user = cursor.fetchall()
            users.append(user[0])
        except sqlite3.Error as e:
            print(f"Errore durante l'esecuzione della query: {e}")
    return users

def control_client(email):
    try:
        query="SELECT id FROM users WHERE email= ?"
        cursor.execute(query,(email,)) #TO_DO andrebbero messe delle stampe per vedere che stiamo facendo
        result=cursor.fetchone()
        print("result ",result)
        if result != None:
            return result
        else:
            return False
    except sqlite3.Error as e:
        print(f"Errore durante l'esecuzione della query: {e}")
   

#la chiamo solo se crasha qualcosa
def crash():
    try:
        conn.close()
    except sqlite3.Error as e:
        print(f"Errore durante la chiusura della connessione al database: {e}")

#FLASK----------------------------------------------------------------------------------
@app.route('/controlla_utente', methods=['GET'])
def controlla_utente():
    email = request.args.get("email")
    id=control_client(email)
    result = {"userid": id}
    return result

@app.route('/registra_utente', methods=['POST'])
def inserisci_utente():
    if request.method == 'POST': 
        data = request.json
        stato = inserisci_client(data["nome"],data["cognome"],data["email"])
        result = {'message': stato, 'data': data}
        return jsonify(result) 
    
@app.route('/trova_email_by_user_id', methods=['POST'])
def trova_utente():
    if request.method == 'POST': 
        data = request.json
        print("json ",data)
        data_dict = json.loads(data)
        print("load ",data_dict)
        emails=get_email_by_userid(*data_dict)
        print("emails ",emails)
        return jsonify(emails)
    
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5001, debug=True, threaded=True)

