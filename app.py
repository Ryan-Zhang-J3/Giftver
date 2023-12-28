from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import re
from random import shuffle

app = Flask(__name__)
#Email Functionality
load_dotenv()

mail = Mail(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

mail = Mail(app)

#Adding DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///participant_list.db'
app.app_context().push()
db = SQLAlchemy(app)

#DB Definition
class ParticipantList(db.Model):
    __tablename__ = 'participant_list'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(60), nullable=False)
    name = db.Column(db.String(60), nullable=False)
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlist.id'))
    wishlist = db.relationship('Wishlist', backref='participant', uselist=False)

    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Participant %r>' % self.id

class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    id = db.Column(db.Integer, primary_key=True)
    wishlist_content = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Wishlist %r>' % self.id

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)
    
#Adding Participant
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        participant_content = request.form['content']
        # Check if the email is valid
        if not is_valid_email(participant_content):
            return 'Invalid email'

        # Check if the email already exists in the database
        existing_participant = ParticipantList.query.filter_by(content=participant_content).first()
        if existing_participant:
            return 'Email already exists in the database'
        
        new_participant = ParticipantList(content=participant_content, name=name)

        # Check if 'wishlist' key is present in the form data
        participant_wishlist = request.form.get('wishlist')
        if participant_wishlist:
            new_wishlist = Wishlist(wishlist_content=participant_wishlist)
            new_participant.wishlist = new_wishlist

        try:
            db.session.add(new_participant)
            db.session.commit()
            return redirect('/')
        except:
            return 'Error adding participant'
    else:
        participants = ParticipantList.query.order_by(ParticipantList.date_created).all()
        return render_template('index.html', participants=participants)
    
#Deleting Participant
@app.route('/delete/<int:id>')
def delete(id):
    participant_to_delete = ParticipantList.query.get_or_404(id)

    try:
        db.session.delete(participant_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'Error deleting participant'


#Updating Participant
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    participant_to_update = ParticipantList.query.get_or_404(id)
    if request.method == 'POST':
        participant_to_update.content = request.form['content']
        participant_to_update.name = request.form['name']
        
        wishlist_value = request.form.get('wishlist')
        if wishlist_value:
            if participant_to_update.wishlist:
                participant_to_update.wishlist.wishlist_content = wishlist_value
            else:
                new_wishlist = Wishlist(wishlist_content=wishlist_value)
                participant_to_update.wishlist = new_wishlist

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'Error updating participant'
    else:
        wishlist_value = participant_to_update.wishlist.wishlist_content if participant_to_update.wishlist else None
        return render_template('update.html', participant=participant_to_update, wishlist=wishlist_value)  


@app.route('/start_gift_exchange')
def start_gift_exchange():
    participants = ParticipantList.query.all()

    # Get the participants' wishlists
    participants_wishlists = {participant.id: participant.wishlist.wishlist_content if participant.wishlist else None for participant in participants}

    # Shuffle the participants
    shuffled_participants = participants.copy()
    shuffle(shuffled_participants)

    # Assign secret Santa recipients
    for i in range(len(participants)):
        participant = shuffled_participants[i]
        recipient = shuffled_participants[(i + 1) % len(participants)]
        participant.recipient_id = recipient.id

    # Send emails to participants
    with mail.connect() as conn:
        for participant in participants:
            recipient = ParticipantList.query.get(participant.recipient_id)
            recipient_name = recipient.name
            recipient_wishlist = participants_wishlists[recipient.id]

            subject = 'Secret Santa Gift Exchange'
            body = f'Hello {participant.name}!\n\nYou have been assigned {recipient_name} as your secret Santa recipient.\nTheir wishlist: {recipient_wishlist}\n\nHappy gifting!'
            msg = Message(subject=subject, body=body, sender=(app.config['MAIL_USERNAME'], "Santa's Elves"), recipients=[participant.content])
            conn.send(msg)
#test
    try:
        db.session.commit()
        return 'Secret Santa gift exchange initiated'
    except:
        return 'Error starting gift exchange'
    

if __name__ == "__main__":
    app.run(debug=True)