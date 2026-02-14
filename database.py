import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = 'alumni_donations.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create donations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            batch_year INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_id TEXT NOT NULL,
            order_id TEXT NOT NULL,
            message TEXT,
            certificate_sent BOOLEAN DEFAULT 0,
            donated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create alumni table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alumni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            batch_year INTEGER NOT NULL,
            phone TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create admin table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create email logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient TEXT NOT NULL,
            subject TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'sent'
        )
    ''')
    
    # Create default admin if not exists
    cursor.execute('SELECT * FROM admins WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        password_hash = generate_password_hash('admin123')
        cursor.execute(
            'INSERT INTO admins (username, password_hash, full_name) VALUES (?, ?, ?)',
            ('admin', password_hash, 'System Administrator')
        )
    
    conn.commit()
    conn.close()
    print("✓ Database initialized successfully")

def add_donation(name, email, batch_year, amount, payment_id, order_id, message=''):
    """Add a new donation record"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO donations (name, email, batch_year, amount, payment_id, order_id, message)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, email, batch_year, amount, payment_id, order_id, message))
    donation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return donation_id

def mark_certificate_sent(donation_id):
    """Mark certificate as sent"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE donations SET certificate_sent = 1 WHERE id = ?', (donation_id,))
    conn.commit()
    conn.close()

def get_all_donations():
    """Get all donations"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM donations ORDER BY donated_at DESC')
    donations = cursor.fetchall()
    conn.close()
    return donations

def get_donation_stats():
    """Get donation statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*), SUM(amount) FROM donations')
    total_count, total_amount = cursor.fetchone()
    
    cursor.execute('SELECT COUNT(DISTINCT batch_year) FROM donations')
    unique_batches = cursor.fetchone()[0]
    
    cursor.execute('SELECT batch_year, COUNT(*), SUM(amount) FROM donations GROUP BY batch_year ORDER BY batch_year DESC')
    batch_stats = cursor.fetchall()
    
    conn.close()
    
    return {
        'total_donations': total_count or 0,
        'total_amount': total_amount or 0,
        'unique_batches': unique_batches or 0,
        'batch_breakdown': batch_stats
    }

def verify_admin(username, password):
    """Verify admin credentials"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM admins WHERE username = ?', (username,))
    admin = cursor.fetchone()
    conn.close()
    
    if admin and check_password_hash(admin['password_hash'], password):
        return {'id': admin['id'], 'username': admin['username'], 'full_name': admin['full_name']}
    return None

def get_alumni_by_batch(batch_year=None):
    """Get alumni filtered by batch"""
    conn = get_db()
    cursor = conn.cursor()
    
    if batch_year:
        cursor.execute('SELECT * FROM alumni WHERE batch_year = ?', (batch_year,))
    else:
        cursor.execute('SELECT * FROM alumni')
    
    alumni = cursor.fetchall()
    conn.close()
    return alumni

def add_email_log(recipient, subject, status='sent'):
    """Log email sending"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO email_logs (recipient, subject, status) VALUES (?, ?, ?)',
        (recipient, subject, status)
    )
    conn.commit()
    conn.close()