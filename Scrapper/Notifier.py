from flask import Flask, jsonify, request
import smtplib

app = Flask(__name__)


#TO_DO verifica invio mail, creazione account invio
#TO-DO potrebbe essere necessario aggiungere un'eccezione per l'utilizzo di applicazioni esterne dalle impostazioni account di posta!
def inviomail(mail,msg):
    # s = smtplib.SMTP(host='your_host_address_here', port=your_port_here)
    # s.starttls()
    # s.login(MY_ADDRESS, PASSWORD)
    # s.sendmail("mittente", mail , messaggio)
    # s.quit
    print(mail)


@app.route('/recuperomail', methods=['POST']) 
def comunicazionepost():
    data,msg = request.form['data,msg'] #TO_DO non sono sicuro che cosi richiede due dati
    inviomail(data,msg)
    return '', 204   