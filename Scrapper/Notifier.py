from flask import Flask, jsonify, request
import smtplib

app = Flask(__name__)


#TO_DO verifica invio mail, creazione account invio
#TO-DO potrebbe essere necessario aggiungere un'eccezione per l'utilizzo di applicazioni esterne dalle impostazioni account di posta!
def inviomail(notifiche):
    # s = smtplib.SMTP(host='your_host_address_here', port=your_port_here)
    # s.starttls()
    # s.login(MY_ADDRESS, PASSWORD)
    # for tupla in notifiche:
        # s.sendmail("mittente", tupla[0] , tupla[1])
    # s.quit
    print(notifiche[0])


@app.route('/recuperomail', methods=['POST']) 
def comunicazionepost():
    notifiche = request.form['notifiche'] #TO_DO non sono sicuro che cosi richiede due dati
    inviomail(notifiche)
    return '', 204   