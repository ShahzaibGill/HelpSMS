import os
import langdetect
import twilio.twiml
from flask import Flask, request, redirect, make_response, session
from translation import detectLanguage, translate
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.environ['SESSION_KEY']
app.permanent_session_lifetime = timedelta(minutes=30)
app.config.from_object(__name__)

@app.route('/', methods=['GET','POST'])
def SMS():
    message = request.values.get('Body', None)
    # Clearing session. lowercase and source detection
    messageTranslated = translate(request.values.get('Body', None),'en')
    if messageTranslated.lower() == "hello" or messageTranslated.lower() == "hi":
        session.clear()

    #Language detection + Mode Question
    try:
        language = session['language']
    except KeyError:
        language = detectLanguage(message)
        session['language'] = language
        respMessage = translate("What is your mode of transportation? Type 1 for driving, 2 for walking, or 3 for transit.",language, 'en')
        resp = twilio.twiml.Response()
        resp.message(respMessage)
        return str(resp)

    # Mode dection + From address
    try:
        mode = session['mode']
    except KeyError:
        if message == '1':
            session['mode'] = 'driving'
        elif message == '2':
            session['mode'] = 'walking'
        elif message == '3':
            session['mode'] = 'transit'
        else:
            respMessage = translate("What is your mode of transportation? Type 1 for driving, 2 for walking, or 3 for transit",language,"en")
            resp = twilio.twiml.Response()
            resp.message(respMessage)
            return str(resp)
        respMessage = translate("Where are you travelling from? Please enter the full address",language,"en")
        resp = twilio.twiml.Response()
        resp.message(respMessage)
        return str(resp)

    # From detection + To address
    try:
        toAddress = session['to']
    except KeyError:
        session['to'] = translate(message, "en", language)
        respMessage = translate("What is your destination? Please enter the full address", language, 'en')
        resp = twilio.twiml.Response()
        resp.message(respMessage)
        return str(resp)
    return "in progress"

if __name__ == "__main__":
    app.run()