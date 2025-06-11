# main.py

from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
DATABASE = 'transport_rfq.db'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS vendors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    phone TEXT,
                    password TEXT,
                    company_name TEXT,
                    gst_number TEXT,
                    address TEXT,
                    vehicle_types TEXT,
                    regions TEXT,
                    pan_number TEXT,
                    bank_details TEXT,
                    contact_person TEXT,
                    contact_phone TEXT,
                    document TEXT
                )''')
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/vendor_section')
def vendor_section():
    return render_template('vendor_section.html')

@app.route('/vendor_registration', methods=['GET', 'POST'])
def vendor_registration():
    if request.method == 'POST':
        data = request.form
        file = request.files['document']
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("""INSERT INTO vendors (name, email, phone, password, company_name, gst_number, address, vehicle_types, 
                    regions, pan_number, bank_details, contact_person, contact_phone, document) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (data['name'], data['email'], data['phone'], data['password'], data['company_name'],
                   data['gst_number'], data['address'], data['vehicle_types'], data['regions'],
                   data['pan_number'], data['bank_details'], data['contact_person'], data['contact_phone'], filepath))
        conn.commit()
        conn.close()
        return redirect(url_for('view_vendors'))

    return render_template('vendor_registration.html')

@app.route('/view_vendors')
def view_vendors():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM vendors")
    vendors = c.fetchall()
    conn.close()
    return render_template('view_vendors.html', vendors=vendors)

@app.route('/create_rfq', methods=['GET', 'POST'])
def create_rfq():
    if request.method == 'POST':
        data = request.form
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''INSERT INTO rfqs (origin, destination, dead_weight, dimensions, material_type, vehicle_size, created_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (data['origin'], data['destination'], data['dead_weight'], data['dimensions'],
                   data['material_type'], data['vehicle_size'], datetime.now().isoformat()))
        rfq_id = c.lastrowid
        conn.commit()

        c.execute("SELECT email FROM vendors")
        vendors = c.fetchall()
        for vendor in vendors:
            print(f"Notification sent to {vendor[0]}: New RFQ ID {rfq_id} available for bidding.")

        conn.close()
        return redirect(url_for('rfq_status'))

    return render_template('create_rfq.html')

@app.route('/rfq_status')
def rfq_status():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM rfqs")
    rfqs = c.fetchall()
    conn.close()
    return render_template('rfq_status.html', rfqs=rfqs)

if __name__ == '__main__':
    app.run(debug=True)
