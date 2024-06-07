from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exists
from flask_socketio import SocketIO, send
from flask_cors import CORS
from datetime import datetime
import pandas as pd
import random
import time
import os
from twilio.rest import Client
import re
import json
import logging
import requests


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sms_user:smsPassword@localhost/sms_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(
    app,
    origins='*',
    methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    supports_credentials=True
)
app.config['CORS_HEADERS'] = 'Content-Type'


# # Set up logging
# logging.basicConfig(level=logging.INFO)

# @app.before_request
# def log_request_info():
#     logging.info(f"Request Headers: {request.headers}")
#     logging.info(f"Request Body: {request.get_data()}")

# @app.after_request
# def log_response_info(response):
#     logging.info(f"Response Status: {response.status}")
#     logging.info(f"Response Headers: {response.headers}")
#     logging.info(f"Response Body: {response.get_data()}")
#     return response

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False, unique=True)
    address = db.Column(db.String(200), nullable=True)
    contact_status = db.Column(db.String(25), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    direction = db.Column(db.String(10), nullable=False)  # 'sent' or 'received'
    body = db.Column(db.String(160), nullable=False)
    from_phone_number = db.Column(db.String(11), nullable=False)

class ContactMeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    last_sent_time = db.Column(db.DateTime, nullable=True)
    last_reply_time = db.Column(db.DateTime, nullable=True)

class Template(db.Model):
    __tablename__ = 'templates'
    id = db.Column(db.Integer, primary_key=True)
    sms_message = db.Column(db.String(255), nullable=False)
    
class Phones(db.Model):
    __tablename__ = 'phones'
    id = db.Column(db.Integer, primary_key=True)
    twilio_phone = db.Column(db.String(11), nullable=False)


class Statuses(db.Model):
    __tablename__ = 'statuses'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(25), nullable=False)

class ResponseTemplate(db.Model):
    __tablename__ = 'responses_templates'
    id = db.Column(db.Integer, primary_key=True)
    sms_message = db.Column(db.String(255), nullable=False)

# Twilio configuration
account_sid = 'ACad25764d323e82dbc76f774cd1747d51'
auth_token = '57af55422e3e202cc120874b8f3be966'
twilio_number = '+18335335918'


client = Client(account_sid, auth_token)
logging.basicConfig()
client.http_client.logger.setLevel(logging.INFO)


def get_phones():
    phones = db.session.query(Phones.twilio_phone).all()
    return phones

def get_message_template():
    templates = db.session.query(Template.sms_message).all()
    templates = [template[0] for template in templates]
    return random.choice(templates) if templates else None

def get_number_of_templates():
    return db.session.query(Template.sms_message).count()


def message_replace(template, name, address):
    # Check if the template contains the {address} placeholder
    if '{address}' in template:
        formatted_message = template.format(name=name, address=address)
    else:
        formatted_message = template.format(name=name)
    return formatted_message

# Function to send SMS
def send_sms(to_number, message_body, from_phone_number):
    message = client.messages.create(
        body=message_body,
        from_=twilio_number,
        to=to_number
    )
    return message.sid

# Function to normalize phone numbers
def normalize_phone_number(phone_number):
    return re.sub(r'\D', '', str(phone_number))


def get_from_phone_number(contact_id):
    # Query the Message table to find the last used from_phone_number for the given contact_id
    last_message = Message.query.filter_by(contact_id=contact_id).order_by(Message.timestamp.desc()).first()
    if last_message:
        return last_message.from_phone_number
    return twilio_number

# Route to send SMS to contacts from spreadsheet
@app.route('/send_bulk_sms', methods=['POST'])
def send_bulk_sms():
    # file = request.files['file']
    contacts = pd.read_excel('C://Users//USER//Desktop//twilio//back_end//contacts.xlsx')
    template_index = 0

    sms_templates = db.session.query(Template.sms_message).all()
    sms_templates = [template[0] for template in sms_templates]

    for _, contact in contacts.iterrows():
        name = contact['Name']
        phone = normalize_phone_number(contact['Phone'])
        address = contact['Address']

        # Check if contact exists in the database
        db_contact = Contact.query.filter(db.func.replace(Contact.phone, '-', '') == phone).first()
        if not db_contact:
            db_contact = Contact(name=name, phone=phone, address=address)
            db.session.add(db_contact)
            db.session.commit()

        if not sms_templates:
            return jsonify({"status": "No templates found in the database!"}), 500

        template = sms_templates[template_index]
        template_index = (template_index + 1) % len(sms_templates)

        message = message_replace(template, name, address)
        print(message)
        # Send SMS
        send_sms(phone, message)
        
        # Store the message details in the database
        timestamp = datetime.now()
        new_message = Message(contact_id=db_contact.id, timestamp=timestamp, direction='sent', body=message, from_phone_number=twilio_number)
        db.session.add(new_message)
        
        # Update last sent time in contact metadata
        contact_meta = ContactMeta.query.filter_by(contact_id=db_contact.id).first()
        if not contact_meta:
            contact_meta = ContactMeta(contact_id=db_contact.id, last_sent_time=timestamp)
        else:
            contact_meta.last_sent_time = timestamp
        db.session.add(contact_meta)

        db.session.commit()
        
        # Wait for 5 seconds before sending the next message
        time.sleep(5)

    return jsonify({"status": "Messages sent successfully!"})

@app.route('/contacts', methods=['GET'])
def get_contacts():
    # Filter contacts that have received messages
    contacts_with_messages = db.session.query(Contact).filter(exists().where(Message.contact_id == Contact.id)).all()
    
    # Convert the filtered contacts into a JSON response
    contacts_json = [{'id': c.id, 'name': c.name, 'phone': c.phone, 'address': c.address} for c in contacts_with_messages]
    
    return jsonify(contacts_json)


@app.route('/statuses', methods=['GET'])
def get_status():
    statuses = Statuses.query.all()
    return jsonify([{'id':s.id, 'status':s.status} for s in statuses])


@app.route('/update_status', methods=['POST'])
def update_status():
    try:
        payload = json.loads(request.data)
        new_status = payload['status']
        phone = payload['phone']
        

        # Find the contact by phone number
        contact = Contact.query.filter_by(phone=phone).first()

        if contact:
            # Update the contact's status
            contact.contact_status = new_status
            db.session.commit()  # Save changes to the database

            return jsonify({"message": "Status updated successfully"}), 200
        else:
            return jsonify({"message": "Contact not found"}), 404
        

    except Exception as e:
        logging.error(f"Error in update_status: {str(e)}")
        return jsonify({"status": "Failed to update status", "error": str(e)}), 500



@app.route('/response_templates', methods=['GET'])
def get_response_templates():
    response_templates = ResponseTemplate.query.all()
    print(response_templates)
    return jsonify([{'id':s.id, 'sms_message':s.sms_message} for s in response_templates])


@app.route('/submit_lead', methods=['POST'])
def create_lead():
    try:
        # Directly get the JSON payload from the request
        payload = request.json
        
        phone = payload.get('phone')
        address = payload.get('address')
        name = payload.get('name')
        contact_id = payload.get('id')
        
        def get_messages(contact_id):
            messages = Message.query.filter_by(contact_id=contact_id).order_by(Message.timestamp.asc()).all()
            return [{
                'id': m.id,
                'contact_id': m.contact_id,
                'timestamp': m.timestamp.isoformat(),
                'direction': m.direction,
                'body': m.body
            } for m in messages]

        chat = get_messages(contact_id)
        chat_str = json.dumps(chat)


        print(f'The Chat History:\n{chat}')

        # Construct the payload to send to the webhook
        hook_load = {
            "phone": phone,
            "address": address,
            "name": name,
            "chat": chat_str
        }

        # Trigger Webhook
        webhook = 'https://workflow-automation.podio.com/catch/7a63k082482cmx2'
        headers = {'Content-Type': 'application/json'}

        # Send the payload as JSON
        trigger = requests.post(webhook, json=hook_load, headers=headers)
        
        if trigger.status_code == 200:
            return jsonify({"status": "Lead created successfully"}), 200
        else:
            logging.error(f"Webhook call failed: {trigger.status_code}, {trigger.text}")
            return jsonify({"status": "Failed to create lead", "error": trigger.text}), 500

    except Exception as e:
        logging.error(f"Error in create lead: {str(e)}")
        return jsonify({"status": "Failed to create lead", "error": str(e)}), 500


@app.route('/messages/<contact_id>', methods=['GET'])
def get_messages(contact_id):
    messages = Message.query.filter_by(contact_id=contact_id).order_by(Message.timestamp.asc()).all()
    return jsonify([{'id': m.id, 'contact_id': m.contact_id, 'timestamp': m.timestamp, 'direction': m.direction, 'body': m.body} for m in messages])



#Route to handle incoming messages from Twilio
@app.route('/sms', methods=['POST'])
def sms_reply():
    sender = request.form.get('From')
    body = request.form.get('Body')
    message_from = request.form.get('From')
    timestamp = datetime.now()
    print(timestamp)

    # Check if contact exists in the database
    db_contact = Contact.query.filter_by(phone=sender).first()
    if not db_contact:
        return jsonify({"status": "Contact not found!"}), 404

    # Store the received message details in the database
    new_message = Message(contact_id=db_contact.id, timestamp=timestamp, direction='received', body=body, from_phone_number=message_from)
    db.session.add(new_message)
    
    # Update last reply time in contact metadata
    contact_meta = ContactMeta.query.filter_by(contact_id=db_contact.id).first()
    if not contact_meta:
        contact_meta = ContactMeta(contact_id=db_contact.id, last_reply_time=timestamp)
    else:
        contact_meta.last_reply_time = timestamp
    db.session.add(contact_meta)

    db.session.commit()

    print("Contact metadata updated:", contact_meta)

    # Prepare the payload for socket.io emission
    socket_payload = {
        'id': new_message.id,
        'contact_id': new_message.contact_id,
        'timestamp': new_message.timestamp,
        'direction': new_message.direction,
        'body': new_message.body
    }
    print("Payload emitted via socket.io:", socket_payload)

    # Emit the message to the corresponding room (contact_id)
    socketio.emit('message', socket_payload, room=db_contact.id)
    print("Message emitted via socket.io")

    return jsonify({"status": "Message received!"})


@app.route('/send_message', methods=['POST'])

def send_message():
    print("Received message request")
    data = request.json
    print("Request data:", data)
    contact_id = data['contact_id']
    body = data['body']

    contact = Contact.query.get(contact_id)
    from_phone_number = get_from_phone_number(contact_id)   # Update this if there are multiple numbers to use
    send_sms(contact.phone, body, from_phone_number)

    timestamp = datetime.now()
    new_message = Message(contact_id=contact_id, body=body, timestamp=timestamp, direction='sent', from_phone_number=from_phone_number)
    db.session.add(new_message)
    db.session.commit()

    socketio.emit('message', {'contact_id': contact_id, 'body': body, 'timestamp': new_message.timestamp})
    response = jsonify({"status": "Message sent successfully!"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, 201




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, port=5000)

