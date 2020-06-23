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

        if message_text == 'ColorImages':
            send_text_message(sender_id,"Upload picture")
        if message_text === 'Neural Style Image':
            send_text_message(sender_id,"Upload Two pictures one by one")

    elif "attachments" in event["message"]:
        #image = event["message"]["attachments"][0]["payload"]["url"]
        content_image_url = event["message"]["attachments"][0]["payload"]["url"]
        style_image_url= event["message"]["attachments"][1]["payload"]["url"]
        print(content_image_url)
        print(style_image_url)
        #send_colored_image(sender_id,image_url)
        send_neural_style_image(sender_id,content_image_url,style_image_url)


"""
def send_colored_image(recipient_id,image_url):
    r = requests.post(
        "https://api.deepai.org/api/colorizer",
        data={
            'image': image_url,
        },
        headers={'api-key': 'f8f549ed-8c2f-4c76-ad8c-78c6df57b511'}
    )

    colored_image = r.json()['output_url']

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type":"image",
                "payload":{
                    "url": colored_image
                }
            }
        }
    })

    
    call_send_api(message_data)
    show_services(recipient_id)

"""  
send_neural_style_image(sender_id,content_image_url,style_image_url):
    r = requests.post(
        "https://api.deepai.org/api/neural-style",
        data={
            'style': content_image_url,
            'content': style_image_url
        },
        headers={'api-key': 'f8f549ed-8c2f-4c76-ad8c-78c6df57b511'}
    )
    colored_image = r.json()['output_url']

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type":"image",
                "payload":{
                    "url": colored_image
                }
            }
        }
    })

    call_send_api(message_data)
    show_services(recipient_id)

def received_postback(event):

    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID

    # The payload param is a developer-defined field which is set in a postback
    # button for Structured Messages
    payload = event["postback"]["payload"]

    if payload == 'Get Started':
        # Get Started button was pressed
         show_services(sender_id)

    else:
        # Notify sender that postback was successful
        send_text_message(sender_id,"Postback successfull")


def send_text_message(recipient_id,message_text):
    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })

    call_send_api(message_data)

def show_services(recipient_id):
    message_data = json.dumps({
        "recipient":{
            "id":recipient_id
        },
        "messaging_type": "RESPONSE",
        "message":{
            "text": "Choose a service",
            "quick_replies":[
                {
                    "content_type":"text",
                    "title":"ColorImages",
                    "payload":"postback",
                },
                {
                    "content_type":"text",
                    "title":"Color extractor",
                    "payload":"postback",
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







