from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import os
import dotenv
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, FloatField, SubmitField
from wtforms.validators import Length, DataRequired, NumberRange
from flask_restful import Api, Resource


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
def read_item(id):
    item = Item.query.get_or_404(id)
    return render_template('read.html', item=item)


@app.route('/update/<int:id>/', methods=['GET', 'POST'])
def update_item(id):
    item = Item.query.get_or_404(id)
    form = ItemForm()
    form.submit.label.text = 'Update'
    if form.validate_on_submit():
        item.name = form.name.data
        item.description = form.description.data
        item.quantity = form.quantity.data
        item.price = form.price.data
        db.session.commit()
        flash('♻️ Item updated successfully!', 'success')
        return redirect(url_for('index'))
    form.name.data = item.name
    form.description.data = item.description
    form.quantity.data = item.quantity
    form.price.data = item.price
    return render_template('update.html', form=form, item=item)


@app.route('/delete/<int:id>/')
def delete_item(id):
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('🗑️ Item deleted successfully!', 'success')
    return redirect(url_for('index'))


# ====================================================================

api = Api(app)

def item_to_dict(item):
    return {
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'quantity': item.quantity,
        'price': item.price,
        'created_at': item.created_at.isoformat()
    }


class ItemListResource(Resource):
    def get(self):
        items = Item.query.order_by(Item.created_at.desc()).all()
        return [item_to_dict(item) for item in items], 200

    def post(self):
        data = request.get_json()
        if not data:
            return {'message': 'No input data provided'}, 400

        name = data.get('name')
        description = data.get('description')
        quantity = data.get('quantity')
        price = data.get('price')

        if not all([name, quantity, price]):
            return {'message': 'Name, quantity, and price are required.'}, 400

        item = Item(name=name, description=description, quantity=quantity, price=price)
        db.session.add(item)
        db.session.commit()
        return item_to_dict(item), 201


class ItemResource(Resource):
    def get(self, item_id):
        item = Item.query.get_or_404(item_id)
        return item_to_dict(item), 200

    def put(self, item_id):
        item = Item.query.get_or_404(item_id)
        data = request.get_json()

        item.name = data.get('name', item.name)
        item.description = data.get('description', item.description)
        item.quantity = data.get('quantity', item.quantity)
        item.price = data.get('price', item.price)

        db.session.commit()
        return item_to_dict(item), 200

    def delete(self, item_id):
        item = Item.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {'message': 'Item deleted successfully.'}, 200


api.add_resource(ItemListResource, '/items')
api.add_resource(ItemResource, '/items/<int:item_id>')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print(' * {0} is active!'.format(app.config['SQLALCHEMY_DATABASE_URI']))
    app.run(debug=True, host='0.0.0.0')