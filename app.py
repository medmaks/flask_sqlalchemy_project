from flask import Flask
from models import db, Store, Item

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

#  Створення таблиць 
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return "Flask + SQLAlchemy працює!"

@app.route("/create")
def create_store_with_items():
    store = Store(name="Мій магазин - RETRON")
    db.session.add(store)
    db.session.commit()

    item1 = Item(name="Молоко", store_id=store.id)
    item2 = Item(name="Хліб", store=store)

    db.session.add(item1)
    db.session.add(item2)
    db.session.commit()

    return f"Додано магазин '{store.name}' з товарами: {item1.name}, {item2.name}"

if __name__ == "__main__":
    app.run(debug=True)
