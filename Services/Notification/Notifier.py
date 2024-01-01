from flask import Flask, request
import smtplib
import json

app = Flask(__name__)


#TO_DO verifica invio mail, creazione account invio
#TO-DO potrebbe essere necessario aggiungere un'eccezione per l'utilizzo di applicazioni esterne dalle impostazioni account di posta!
def inviomail(notifiche):
    try:
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.starttls()
    except smtplib.SMTPConnectError as error:
        print(f"Errore durante la connessione a gmail: {error}")
        return 'error'
    try: 
        mail.login('notifier.dsbd@gmail.com', 'sywb dxem iyph awkk')
    except smtplib.SMTPAuthenticationError as error:
        print(f"Errore durante l'esecuzione della query: {error}")
        return 'error'
    for tupla in notifiche:
        try:
            print("la tupla completa ",tupla)
            email=tupla['email']
            messaggio=json.dumps(tupla['message'])
            body = f"Caro {email} ,\n questa e' l'offerta da te richiesta\n {messaggio}"
            print("mail ",email)
            print("body ",body)
            mail.sendmail("Notifier.dsbd@gmail.com", email, body)
        except smtplib.SMTPDataError as error:
            print(f"Errore durante l'esecuzione della query: {error}")
            return 'error'    
    mail.close()
    return 'ok'


@app.route('/recuperomail', methods=['POST']) 
def comunicazionepost():
    notifiche = request.json
    stato=inviomail(notifiche['notifiche'])
    return stato  

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5003, debug=True, threaded=True)