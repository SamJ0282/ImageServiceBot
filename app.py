import os, sys
from flask import Flask, request
from pymessenger import Bot

from clarifai.rest import ClarifaiApp
from clarifai.rest import Image
import json
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def verify():
	# Webhook verification
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello world", 200


@app.route('/', methods=['POST'])   
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
      # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":   # make sure this is a page subscription

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):     # someone sent us a message
                    received_message(messaging_event)
                    # received_authentication(messaging_event)

                elif messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    received_postback(messaging_event)

                else:    # uknown messaging_event
                    pass

    return "ok", 200

def received_message(event):

    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    
    # could receive text or attachment but not both
    if "text" in event["message"]:
        message_text = event["message"]["text"]
        print(message_text)

    elif "attachments" in event["message"]:
        image_url = event["message"]["attachments"][0]["payload"]["url"]
        send_color_message(sender_id, image_url)


"""
def send_generic_message(recipient_id):

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [{
                        "title": "Asylex",
                        "subtitle": "free online legal aid on Swiss asylum law",
                        "item_url": "https://asylex.ch/",               
                        "image_url": "https://www.google.ch/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png",
                        "buttons": [{
                            "type": "web_url",
                            "url": "https://asylex.ch/docs/faq_en.pdf",
                            "title": "Open FAQ"
                        }, {
                            "type": "postback",
                            "title": "Call Postback",
                            "payload": "Payload for first bubble",
                        }],
                    }, {
                        "title": "Google",
                        "subtitle": "Find all your answers",
                        "item_url": "https://www.google.com/",               
                        "image_url": "https://www.google.ch/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png",
                        "buttons": [{
                            "type": "web_url",
                            "url": "https://www.google.ch/",
                            "title": "Google Suche"
                        }, {
                            "type": "postback",
                            "title": "Call Postback",
                            "payload": "Payload for second bubble",
                        }]
                    }]
                }
            }
        }
    })

    

    call_send_api(message_data)
"""

#RECIEVE IMAGE FROM USER
def send_color_message(recipient_id,image_url):
    app = ClarifaiApp(api_key = os.environ["CLARIFAI_API_KEY"])
    model = app.models.get('color')

    image = Image(url = image_url)
    response = model.predict([image])

    outputs = response["outputs"]
    color_list= []

    for i in outputs:
        color_list.append(i["data"]["colors"])

    colors = []
    for j in color_list[0]:
        colors.append(j["w3c"]["name"])

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": "{}".format(colors)
        }
    })

    call_send_api(message_data)
    
 
#USING CLARIFAI API
"""
def get_color(recipient_id):
    app = ClarifaiApp(api_key = os.environ["CLARIFAI_API_KEY"])
    model = app.models.get('color')

    image = Image(url='https://samples.clarifai.com/metro-north.jpg')
    response = model.predict([image])

    outputs = response["outputs"]
    color_list= []

    for i in outputs:
        color_list.append(i["data"]["colors"])

    colors = []
    for j in color_list[0]:
        colors.append(j["w3c"]["name"])

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": "{}".format(colors)
        }
    })

    call_send_api(message_data)
"""

"""
def send_text_message(recipient_id, message_text):

    # encode('utf-8') included to log emojis to heroku logs
    
    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })

    call_send_api(message_data)


"""
    


#SEND API
def call_send_api(message_data):

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    r = requests.post("https://graph.facebook.com/v7.0/me/message_attachments", params=params, headers=headers, data=message_data)
    


if __name__ == "__main__":
	app.run(debug = True, port = 80)
