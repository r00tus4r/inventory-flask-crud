from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import dotenv
from datetime import datetime

dotenv.load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-fallback-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'

db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Item {self.id}>'

@app.route('/')
def index():
    items = Item.query.order_by(Item.created_at.desc()).all()
    return render_template('index.html', items=items)

@app.route('/create', methods=['GET', 'POST'])
def create_item(): return 'create item'

@app.route('/read/<int:id>/')
def read_item(id): return 'read item'

@app.route('/update/<int:id>/', methods=['GET', 'POST'])
def update_item(id): return 'update item'

@app.route('/delete/<int:id>/')
def delete_item(id): return 'delete item'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print(' * {0} is active!'.format(app.config['SQLALCHEMY_DATABASE_URI']))
    app.run(debug=True, host='0.0.0.0')