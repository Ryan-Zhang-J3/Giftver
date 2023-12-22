from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


@app.before_first_request
def create_tables():
    db.create_all()


app = Flask(__name__)
app.app_context()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.app_context().push()
db = SQLAlchemy(app)


class ParticipantList(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(60), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)

    #returning string of new entry 
    def __repr__(self):
        return '<Participant %r>' % self.id
    
@app.route('/', methods=['POST', 'GET'])

def index():
    if request.method == 'POST':
        giftlist_content = request.form['content']
        new_participant = ParticipantList(content=giftlist_content)
        try:
            db.session.add(new_participant)
            db.session.commit()
            return redirect('/')
        except:
            return "There was an error adding your Participant"

    else:
        participants = ParticipantList.query.order_by(ParticipantList.date_created).all()
        return render_template('index.html', participants = participants)

if __name__ == "__main__":
    app.run(debug=True)