from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super-secret-key"  # У виробничій системі використовуйте більш надійний ключ

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Модель користувача
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

with app.app_context():
    db.create_all()

# Ендпоінт реєстрації
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        # Відображення сторінки з формою реєстрації
        return render_template_string("""
            <h2>Реєстрація</h2>
            <form method="post" action="/register">
              <input type="text" name="username" placeholder="Ім'я користувача" required><br>
              <input type="password" name="password" placeholder="Пароль" required><br>
              <button type="submit">Зареєструватися</button>
            </form>
            <br>
            <a href="/login">Вже зареєстровані? Увійти</a>
        """)
    else:
        # Обробка POST-запиту. Перевіряємо, чи дані надходять у форматі JSON чи як дані форми
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"msg": "Потрібно вказати username та password"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"msg": "Користувач з таким ім'ям вже існує"}), 400

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Якщо реєстрація пройшла через форму, перенаправляємо на сторінку входу
        if request.is_json:
            return jsonify({"msg": "Користувача успішно створено"}), 201
        else:
            return redirect(url_for("login"))

# Ендпоінт входу
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # Відображення сторінки з формою входу
        return render_template_string("""
            <h2>Вхід</h2>
            <form method="post" action="/login">
              <input type="text" name="username" placeholder="Ім'я користувача" required><br>
              <input type="password" name="password" placeholder="Пароль" required><br>
              <button type="submit">Увійти</button>
            </form>
            <br>
            <a href="/register">Зареєструватися</a>
        """)
    else:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            if request.is_json:
                return jsonify({"msg": "Невірне ім'я користувача або пароль"}), 401
            else:
                return render_template_string("""
                    <h3>Невірне ім'я користувача або пароль</h3>
                    <a href='/login'>Спробувати ще раз</a>
                """)

        # Генеруємо access_token, перетворюючи user.id на рядок
        access_token = create_access_token(identity=str(user.id))

        if request.is_json:
            return jsonify({"access_token": access_token}), 200
        else:
            return render_template_string(f"""
                <h3>Вхід виконано успішно!</h3>
                <p>Ваш токен: {access_token}</p>
                <a href="/">Перейти на головну сторінку</a>
            """)

# Захищений ендпоінт
@app.route("/")
@jwt_required()
def home():
    return render_template_string("""
        <h2>Головна сторінка</h2>
        <p>Ви успішно аутентифіковані!</p>
        <ul>
            <li><a href="/some_protected_endpoint">Інший захищений ендпоінт</a></li>
        </ul>
    """)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
