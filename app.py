from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///participant_list.db'
app.app_context().push()
db = SQLAlchemy(app)

class ParticipantList(db.Model):
    __tablename__ = 'participant_list'
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(60), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)

    #returning string of new entry 
    def __repr__(self):
        return '<Participant %r>' % self.id
    
@app.route('/', methods=['POST', 'GET'])

def index():
    if request.method == 'POST':
        participant_content = request.form['content']
        new_participant = ParticipantList(content=participant_content)
        
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

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'Error updating participant email'
    else:
        return render_template('update.html', participant=participant_to_update)
    
    
if __name__ == "__main__":
    app.run(debug=True)