from flask import Flask, jsonify, request
import smtplib

app = Flask(__name__)


#TO_DO verifica invio mail, creazione account invio
#TO-DO potrebbe essere necessario aggiungere un'eccezione per l'utilizzo di applicazioni esterne dalle impostazioni account di posta!
def inviomail(notifiche):
    try:
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.starttls()
    except smtplib.SMTPConnectError as error:
        print("Errore durante l'esecuzione della query: {e}")
        return 'error'
    try: 
        mail.login('Notifier.dsbd@gmail.com', '@cUhTt!r5F')
    except smtplib.SMTPAuthenticationError as error:
        print("Errore durante l'esecuzione della query: {e}")
        return 'error'
    for tupla in notifiche:
        try:
            print("la tupla completa ",tupla)
            body = f"Caro {tupla['email']} ,\n questa è l'offerta da te richiesta\n {tupla['message']}"
            mail.sendmail("Notifier.dsbd@gmail.com", tupla['email'] , body)
        except smtplib.SMTPDataError as error:
            print("Errore durante l'esecuzione della query: {e}")
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