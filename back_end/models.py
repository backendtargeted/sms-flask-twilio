from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
