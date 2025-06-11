from flask import Flask, request, jsonify, render_template_string, redirect
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
DATABASE = 'transport_rfq.db'

# ✅ Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # Vendors Table
    c.execute('''CREATE TABLE IF NOT EXISTS vendors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    phone TEXT,
                    password TEXT
                )''')
    # RFQ Table
    c.execute('''CREATE TABLE IF NOT EXISTS rfqs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    origin TEXT,
                    destination TEXT,
                    dead_weight REAL,
                    dimensions TEXT,
                    material_type TEXT,
                    vehicle_size TEXT,
                    created_at TEXT
                )''')
    # Bids Table
    c.execute('''CREATE TABLE IF NOT EXISTS bids (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rfq_id INTEGER,
                    vendor_id INTEGER,
                    bid_amount REAL,
                    bid_time TEXT
                )''')
    conn.commit()
    conn.close()

if not os.path.exists(DATABASE):
    init_db()

# ✅ Homepage UI with sections
@app.route('/')
def home():
    html = '''
    <html>
        <head>
            <title>Welcome to Buckle Track</title>
        </head>
        <body style="font-family: Arial; text-align: center; margin-top: 30px;">
            <h1>🚚 Welcome to Buckle Track - Transportation RFQ System</h1>
            <hr><br>
            <a href="/vendors"><button style="padding:10px 20px;margin:10px;">👤 Vendor Section</button></a>
            <a href="/rfq_form"><button style="padding:10px 20px;margin:10px;">📝 Create RFQ</button></a>
            <a href="/status"><button style="padding:10px 20px;margin:10px;">📊 Status Section</button></a>
        </body>
    </html>
    '''
    return render_template_string(html)

# ✅ View Vendors
@app.route('/vendors')
def vendors():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id, name, email, phone FROM vendors")
    vendors = c.fetchall()
    conn.close()

    html = "<h2>Registered Vendors</h2><ul>"
    for v in vendors:
        html += f"<li><b>ID:</b> {v[0]} | <b>Name:</b> {v[1]} | <b>Email:</b> {v[2]} | <b>Phone:</b> {v[3]}</li>"
    html += "</ul><br><a href='/'><button>🏠 Back to Home</button></a>"
    return render_template_string(html)

# ✅ RFQ Form
@app.route('/rfq_form', methods=['GET', 'POST'])
def rfq_form():
    if request.method == 'POST':
        data = request.form
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''INSERT INTO rfqs (origin, destination, dead_weight, dimensions, material_type, vehicle_size, created_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (data['origin'], data['destination'], data['weight'], data['dimensions'],
                   data['material'], data['vehicle'], datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return redirect('/status')

    html = '''
    <h2>Create RFQ</h2>
    <form method="POST">
        <input name="origin" placeholder="Origin" required><br><br>
        <input name="destination" placeholder="Destination" required><br><br>
        <input name="vehicle" placeholder="Vehicle Type" required><br><br>
        <input name="weight" placeholder="Dead Weight (kg)" required><br><br>
        <input name="dimensions" placeholder="Product Dimensions (LxWxH)" required><br><br>
        <input name="material" placeholder="Material Type" required><br><br>
        <button type="submit">Submit RFQ</button>
    </form>
    <br><a href='/'><button>🏠 Back to Home</button></a>
    '''
    return render_template_string(html)

# ✅ Status Section
@app.route('/status')
def status():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM rfqs ORDER BY id DESC LIMIT 5")
    rfqs = c.fetchall()

    c.execute("SELECT * FROM bids ORDER BY bid_time DESC LIMIT 5")
    bids = c.fetchall()
    conn.close()

    html = "<h2>RFQ Status (Latest)</h2><ul>"
    for r in rfqs:
        html += f"<li>📦 ID: {r[0]}, From: {r[1]} → {r[2]}, Vehicle: {r[6]}, Time: {r[7]}</li>"
    html += "</ul>"

    html += "<h2>Vendor Bids (Latest)</h2><ul>"
    for b in bids:
        html += f"<li>💰 RFQ ID: {b[1]}, Vendor ID: {b[2]}, Bid: ₹{b[3]}, Time: {b[4]}</li>"
    html += "</ul><br>"

    html += "<a href='/'><button>🏠 Back to Home</button></a>"
    return render_template_string(html)

# ✅ Register Vendor API
@app.route('/register', methods=['POST'])
def register_vendor():
    data = request.json
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO vendors (name, email, phone, password) VALUES (?, ?, ?, ?)",
              (data['name'], data['email'], data['phone'], data['password']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Vendor registered successfully"}), 201

# ✅ API to submit bid
@app.route('/submit_bid', methods=['POST'])
def submit_bid():
    data = request.json
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''INSERT INTO bids (rfq_id, vendor_id, bid_amount, bid_time)
                 VALUES (?, ?, ?, ?)''',
              (data['rfq_id'], data['vendor_id'], data['bid_amount'], datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({"message": "Bid submitted successfully"}), 201

# ✅ View all RFQs (API)
@app.route('/get_rfqs', methods=['GET'])
def get_rfqs():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM rfqs")
    rfqs = c.fetchall()
    conn.close()
    return jsonify(rfqs)

# ✅ View Bids for an RFQ
@app.route('/get_bids/<int:rfq_id>', methods=['GET'])
def get_bids(rfq_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM bids WHERE rfq_id = ?", (rfq_id,))
    bids = c.fetchall()
    conn.close()
    return jsonify(bids)

# ✅ Run app (for local testing only)
if __name__ == '__main__':
    app.run(debug=True)
