import os, sys
from flask import Flask, request
from pymessenger import Bot

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
        
        if message_text == 'stores':
            send_store_names(sender_id)

    elif "attachments" in event["message"]:
        pass
        




def send_store_names(recipient_id):
    message_data = json.dumps({
        "recipient_id":{
            "id":recipient_id
        },
        "messaging_type": "RESPONSE",
        "message":{
            "text": "Available stores",
            "quick_replies":[
                {
                    "content_type":"text",
                    "title":"Shop A",
                    "payload":"<POSTBACK_PAYLOAD>",
                },
                {
                    "content_type":"text",
                    "title":"Shop B",
                    "payload":"<POSTBACK_PAYLOAD>",
                }
            ]
        }
    })

    call_send_api(message_data)
    


def call_send_api(message_data):

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    r = requests.post("https://graph.facebook.com/v7.0/me/messages", params=params, headers=headers, data=message_data)
    


if __name__ == "__main__":
	app.run(debug = True, port = 80)
