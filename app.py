from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import dotenv
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, FloatField, SubmitField
from wtforms.validators import Length, DataRequired, NumberRange


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


class ItemForm(FlaskForm):
    name = StringField(
        'Name',
        validators=[
            DataRequired(message='Name is required.'),
            Length(min=1, max=120, message='Name must be between 1 and 120 characters.')
        ],
        description='Enter the name of the item (max 120 characters).'
    )
    
    description = TextAreaField(
        'Description',
        validators=[],
        description='Optional: add a description for the item.'
    )
    
    quantity = IntegerField(
        'Quantity',
        validators=[
            DataRequired(message='Quantity is required.'),
            NumberRange(min=1, message='Quantity must be at least 1.')
        ],
        description='Enter the available quantity (must be 1 or more).'
    )
    
    price = FloatField(
        'Price',
        validators=[
            DataRequired(message='Price is required.'),
            NumberRange(min=0.1, message='Price must be at least $0.10.')
        ],
        description='Enter the item price in USD.'
    )
    
    submit = SubmitField('Submit')


@app.route('/')
def index():
    items = Item.query.order_by(Item.created_at.desc()).all()
    return render_template('index.html', items=items)


@app.route('/create', methods=['GET', 'POST'])
def create_item():
    form = ItemForm()
    form.submit.label.text = 'Create'
    if form.validate_on_submit():
        item = Item(name=form.name.data, description=form.description.data, quantity=form.quantity.data, price=form.price.data)
        db.session.add(item)
        db.session.commit()
        flash('✅ Item created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('create.html', form=form)


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