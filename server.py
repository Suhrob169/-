"""
SERVER.PY — Бэкенд и Админка для PARVINA CAKES.
Запуск: python server.py
"""
import os, sqlite3, time, urllib.parse, urllib.request
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DB = "orders.db"

# ═══ НАСТРОЙКИ TELEGRAM ═══
# Я уже вставил ваш токен сюда. Осталось только вписать ваш CHAT_ID (цифры).
BOT_TOKEN = "9025892764:AAF9Y_z1j1FMHhZpBoAKZoSnqBNSyFVj0"
CHAT_ID = "ВАШ_ЧАТ_ID_ЦИФРАМИ" 
# ==========================

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, phone TEXT, address TEXT, items TEXT, total REAL, created TEXT);
    """)
    con.commit()
    con.close()

init_db()

def send_tg(msg):
    if CHAT_ID == "ВАШ_ЧАТ_ID_ЦИФРАМИ":
        print("Telegram не настроен: не указан CHAT_ID")
        return
    try:
        text = urllib.parse.quote(msg)
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}"
        urllib.request.urlopen(url)
    except Exception as e:
        print("Ошибка Telegram:", e)

@app.route("/api/order", methods=["POST"])
def order():
    d = request.get_json(force=True)
    cart = d.get("cart", [])
    name = d.get("name")
    phone = d.get("phone")
    address = d.get("address", "Самовывоз")
    
    if not cart or not name or not phone:
        return jsonify(error="Ошибка данных"), 400
        
    lines = [f"• {i['name']} x {i['qty']} = {i['price']*i['qty']} сом." for i in cart]
    total = sum(i['price']*i['qty'] for i in cart)
    items_text = "\n".join(lines)
    
    con = db()
    cur = con.execute("INSERT INTO orders(name,phone,address,items,total,created) VALUES(?,?,?,?,?,?)",
                      (name, phone, address, items_text, total, time.strftime("%Y-%m-%d %H:%M")))
    con.commit()
    oid = cur.lastrowid
    con.close()

    # Отправка уведомления в Telegram
    tg_msg = f"🛒 НОВЫЙ ЗАКАЗ №{oid}!\n\nКлиент: {name}\nТел: {phone}\nАдрес: {address}\n\n{items_text}\n\n💰 Итого: {total} сом."
    send_tg(tg_msg)

    return jsonify(ok=True, id=oid, total=total)

ADMIN_HTML = """
<!doctype html><html><head><meta charset="utf-8"><title>Заказы</title>
<style>body{font-family:sans-serif;padding:20px;background:#f4f4f9}h1{color:#8e1b47}.card{background:#fff;padding:20px;margin-bottom:15px;border-radius:15px;box-shadow:0 4px 10px rgba(0,0,0,0.05);border-left:5px solid #8e1b47}pre{background:#f9f9f9;padding:10px;border-radius:8px;white-space:pre-wrap}.total{font-size:1.2rem;font-weight:bold;color:#8e1b47}</style>
</head><body>
<h1>Панель заказов PARVINA CAKES</h1>
{% for o in orders %}
<div class="card">
    <h3>Заказ №{{ o.id }} <small style="color:#888;font-size:0.8rem;font-weight:normal">({{ o.created }})</small></h3>
    <p><b>Клиент:</b> {{ o.name }} <br><b>Тел:</b> {{ o.phone }}<br><b>Куда:</b> {{ o.address }}</p>
    <pre>{{ o.items }}</pre>
    <p class="total">Итого: {{ o.total }} сом.</p>
</div>
{% else %}<p>Заказов пока нет.</p>{% endfor %}
</body></html>
"""

@app.route("/admin")
def admin():
    con = db()
    orders = con.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    con.close()
    return render_template_string(ADMIN_HTML, orders=orders)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
