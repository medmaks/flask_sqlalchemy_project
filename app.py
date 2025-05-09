from flask import Flask, url_for
from models import db, Store, Item  # Переконайтеся, що models.py знаходиться в тому ж каталозі

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Створення таблиць
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    banner = """
    ================================
          Flask + SQLAlchemy
              Навчальний проєкт
    ================================
    """
    # Генеруємо навігаційні гіперпосилання за допомогою url_for
    links_html = f"""
    <nav>
      <ul>
          <li><a href="{url_for('create_store_with_items')}">Створити магазин та додати товари</a></li>
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

@app.route("/items")
def list_items():
    items = Item.query.all()
    if not items:
        return "Ще немає жодного товару в базі."

    item_list = "<br>".join(f"{item.id}. {item.name} (Магазин ID: {item.store_id})" for item in items)
    return f"<h3>Всі товари в базі:</h3><br>{item_list}"

@app.route("/about")
def about():
    return "<h3>FLASK_SQLALCHEMY_PROJECT-1</h3><p>Легка база на Flask + SQLite для навчання та тестів.</p>"

if __name__ == "__main__":
    print("""
    =========================================
              Стартує Flask-проєкт
    =========================================
    """)
    app.run(debug=True)