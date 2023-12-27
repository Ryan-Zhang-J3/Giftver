from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///participant_list.db'
app.app_context().push()
db = SQLAlchemy(app)

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
    

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        participant_content = request.form['content']
        # Check if the email is valid
        if not is_valid_email(participant_content):
            return 'Invalid email'

        # Check if the email already exists in the database
        existing_participant = ParticipantList.query.filter_by(content=participant_content).first()
        if existing_participant:
            return 'Email already exists in the database'
        
        new_participant = ParticipantList(content=participant_content)

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
    

@app.route('/delete/<int:id>')
def delete(id):
    participant_to_delete = ParticipantList.query.get_or_404(id)

    try:
        db.session.delete(participant_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'Error deleting participant'
    
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    participant_to_update = ParticipantList.query.get_or_404(id)
    if request.method == 'POST':
        participant_to_update.content = request.form['content']
        
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
    
# Existing code...  
if __name__ == "__main__":
    app.run(debug=True)