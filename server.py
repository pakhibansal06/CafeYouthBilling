from flask import Flask, render_template, request, jsonify
import sqlite3
import datetime

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('cafe.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    # This is the main page for Phone and PC
    return render_template('index.html')

@app.route('/api/menu')
def get_menu():
    conn = get_db()
    raw_items = conn.execute("SELECT name, price FROM menu").fetchall()
    conn.close()
    
    processed_items = []
    
    # --- TEMPORARY PRICE HIKE LOOP START ---
    for row in raw_items:
        name = row['name']
        price = row['price']
        
        if price <= 150:
            price += 20
        else:
            price += 30
            
        processed_items.append({"name": name, "price": price})
    # --- TEMPORARY PRICE HIKE LOOP END ---

    return jsonify(processed_items)

@app.route('/api/save_order', methods=['POST'])
def save_order():
    data = request.json # List of items from phone/PC
    conn = get_db()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for item in data:
        conn.execute("INSERT INTO sales (item_name, quantity, total_price, date) VALUES (?, ?, ?, ?)",
                     (item['name'], item['qty'], item['total'], now))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/reports')
def get_reports():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    today_total = conn.execute("SELECT SUM(total_price) FROM sales WHERE date LIKE ?", (f"{today}%",)).fetchone()[0] or 0
    recent = conn.execute("SELECT item_name, quantity, total_price, date FROM sales ORDER BY id DESC LIMIT 10").fetchall()
    conn.close()
    return jsonify({
        "today_total": today_total,
        "recent": [dict(row) for row in recent]
    })
    
# Remove both old IF blocks and replace with this:
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)