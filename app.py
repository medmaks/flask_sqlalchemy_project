from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ======= Моделі =======

# Таблиця-зв’язок
item_category = db.Table("item_category",
    db.Column("item_id", db.Integer, db.ForeignKey("item.id"), primary_key=True),
    db.Column("category_id", db.Integer, db.ForeignKey("category.id"), primary_key=True)
)

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    items = db.relationship("Item", backref="store", lazy=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("store.id"), nullable=False)
    categories = db.relationship("Category", secondary=item_category, backref="items")

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

# =======================

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    banner = """
    ================================
          Flask + SQLAlchemy
              Практична 4
    ================================
    """
    links_html = f"""
    <nav>
      <ul>
          <li><a href="{url_for('create_store_with_items')}">Створити магазин та товари</a></li>
          <li><a href="{url_for('create_categories')}">Створити категорії та призначити товари</a></li>
          <li><a href="{url_for('list_items')}">Список товарів</a></li>
          <li><a href="{url_for('about')}">Про проєкт</a></li>
      </ul>
    </nav>
    """
    return f"<pre>{banner}</pre><h3>Проєкт працює!</h3>{links_html}"

@app.route("/create")
def create_store_with_items():
    store = Store(name="Мій магазин - RETRON")
    db.session.add(store)
    db.session.commit()

    items = ["Молоко", "Хліб", "Сир", "Кефір"]
    added_items = []

    for item_name in items:
        item = Item(name=item_name, store=store)
        db.session.add(item)
        added_items.append(item_name)

    db.session.commit()

    items_list = "<br>".join(f"- {name}" for name in added_items)
    return f"Додано магазин '<b>{store.name}</b>' з товарами:<br>{items_list}"

@app.route("/categories")
def create_categories():
    # Створення категорій
    category1 = Category(name="Напої")
    category2 = Category(name="Молочні продукти")

    db.session.add_all([category1, category2])
    db.session.commit()

    # Призначаємо товари категоріям
    milk = Item.query.filter_by(name="Молоко").first()
    kefir = Item.query.filter_by(name="Кефір").first()

    if milk and kefir:
        milk.categories.append(category2)
        kefir.categories.extend([category1, category2])

        db.session.commit()
        return "Категорії створено та призначено товарам."
    else:
        return "Спочатку додайте товари на /create."

@app.route("/items")
def list_items():
    items = Item.query.all()
    if not items:
        return "Ще немає жодного товару в базі."

    result = ""
    for item in items:
        categories = ", ".join(cat.name for cat in item.categories) if item.categories else "Немає категорій"
        result += f"{item.id}. {item.name} (Магазин ID: {item.store_id}) — {categories}<br>"

    return f"<h3>Всі товари в базі:</h3><br>{result}"

@app.route("/about")
def about():
    return "<h3>FLASK_SQLALCHEMY_PROJECT-1</h3><p>Практична робота 4: Many-to-Many на Flask + SQLite для навчання.</p>"

if __name__ == "__main__":
    print("""
    =========================================
              Стартує Flask-проєкт
    =========================================
    """)
    app.run(debug=True)
