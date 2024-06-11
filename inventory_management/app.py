from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    perishable = db.Column(db.Boolean, default=False)
    expiry_date = db.Column(db.String(10), nullable=True)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    ingredients = db.Column(db.String(200), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/inventory')
def inventory_page():
    return render_template('inventory.html')

@app.route('/get_inventory', methods=['GET'])
def get_inventory():
    inventory = InventoryItem.query.all()
    inventory_list = [{
        'name': item.name,
        'quantity': item.quantity,
        'category': item.category,
        'perishable': item.perishable,
        'expiry_date': item.expiry_date
    } for item in inventory]
    return jsonify(inventory_list)

@app.route('/add_item', methods=['POST'])
def add_item():
    data = request.get_json()
    new_item = InventoryItem(
        name=data['name'],
        quantity=data['quantity'],
        category=data['category'],
        perishable=data['perishable'],
        expiry_date=data['expiry_date'] if data['perishable'] else None
    )
    db.session.add(new_item)
    db.session.commit()
    return get_inventory()

@app.route('/remove_item', methods=['POST'])
def remove_item():
    data = request.get_json()
    item = InventoryItem.query.filter_by(name=data['name']).first()
    if item:
        db.session.delete(item)
        db.session.commit()
    return get_inventory()

@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    data = request.get_json()
    item = InventoryItem.query.filter_by(name=data['name']).first()
    if item:
        item.quantity = data['quantity']
        db.session.commit()
    return get_inventory()

@app.route('/possible_recipes', methods=['GET'])
def possible_recipes():
    inventory = InventoryItem.query.all()
    recipes = get_possible_recipes(inventory)
    return jsonify(recipes)

def get_possible_recipes(inventory):
    recipes = [
        {"name": "Recipe 1", "ingredients": {"item1": 1, "item2": 2}},
        {"name": "Recipe 2", "ingredients": {"item3": 1, "item2": 1}},
    ]
    possible_recipes = []
    for recipe in recipes:
        can_make = True
        for ingredient, amount in recipe["ingredients"].items():
            if not any(item.name == ingredient and item.quantity >= amount for item in inventory):
                can_make = False
                break
        if can_make:
            possible_recipes.append(recipe)
    return possible_recipes

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
