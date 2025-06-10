# main.py

from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = 'transport_rfq.db'

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

@app.before_first_request
def setup():
    init_db()

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

@app.route('/create_rfq', methods=['POST'])
def create_rfq():
    data = request.json
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''INSERT INTO rfqs (origin, destination, dead_weight, dimensions, material_type, vehicle_size, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (data['origin'], data['destination'], data['dead_weight'], data['dimensions'],
               data['material_type'], data['vehicle_size'], datetime.now().isoformat()))
    rfq_id = c.lastrowid
    conn.commit()

    # Notify all vendors (simulated)
    c.execute("SELECT email FROM vendors")
    vendors = c.fetchall()
    for vendor in vendors:
        print(f"Notification sent to {vendor[0]}: New RFQ ID {rfq_id} available for bidding.")

    conn.close()
    return jsonify({"message": f"RFQ {rfq_id} created and vendors notified"}), 201

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

@app.route('/get_rfqs', methods=['GET'])
def get_rfqs():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM rfqs")
    rfqs = c.fetchall()
    conn.close()
    return jsonify(rfqs)

@app.route('/get_bids/<int:rfq_id>', methods=['GET'])
def get_bids(rfq_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM bids WHERE rfq_id = ?", (rfq_id,))
    bids = c.fetchall()
    conn.close()
    return jsonify(bids)
