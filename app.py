from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import socket
import re
import os

app = Flask(__name__)
# Use environment variable for secret key in production, fallback to random for development
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

DATABASE = 'wol_site.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Devices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            mac_address TEXT NOT NULL,
            ip_address TEXT,
            port INTEGER DEFAULT 9,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def validate_mac_address(mac):
    """Validate MAC address format"""
    # Accept formats: XX:XX:XX:XX:XX:XX, XX-XX-XX-XX-XX-XX, XXXXXXXXXXXX
    mac = mac.replace(':', '').replace('-', '').upper()
    if len(mac) != 12:
        return None
    if not all(c in '0123456789ABCDEF' for c in mac):
        return None
    return mac

def send_wol_packet(mac_address, ip_address='255.255.255.255', port=9):
    """Send Wake-on-LAN magic packet"""
    try:
        # Clean MAC address
        mac = validate_mac_address(mac_address)
        if not mac:
            return False, "Adresse MAC invalide"
        
        # Convert MAC to bytes
        mac_bytes = bytes.fromhex(mac)
        
        # Create magic packet: 6 bytes of FF followed by MAC address repeated 16 times
        magic_packet = b'\xff' * 6 + mac_bytes * 16
        
        # Send packet
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, (ip_address, port))
        sock.close()
        
        return True, "Paquet WOL envoyé avec succès"
    except Exception:
        # Don't expose internal exception details to users
        return False, "Erreur lors de l'envoi du paquet WOL"

# Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not username or not email or not password:
            flash('Tous les champs sont requis.', 'danger')
            return redirect(url_for('register'))
        
        if len(username) < 3:
            flash('Le nom d\'utilisateur doit contenir au moins 3 caractères.', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères.', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return redirect(url_for('register'))
        
        # Email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash('Adresse email invalide.', 'danger')
            return redirect(url_for('register'))
        
        # Check if user exists
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        if cursor.fetchone():
            flash('Ce nom d\'utilisateur ou email est déjà utilisé.', 'danger')
            conn.close()
            return redirect(url_for('register'))
        
        # Create user
        hashed_password = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                      (username, email, hashed_password))
        conn.commit()
        conn.close()
        
        flash('Compte créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Tous les champs sont requis.', 'danger')
            return redirect(url_for('login'))
        
        # Check credentials
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Bienvenue, {user["username"]} !', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with devices"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM devices WHERE user_id = ? ORDER BY created_at DESC',
                  (session['user_id'],))
    devices = cursor.fetchall()
    conn.close()
    
    return render_template('dashboard.html', devices=devices)

@app.route('/add-device', methods=['GET', 'POST'])
@login_required
def add_device():
    """Add new device"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        mac_address = request.form.get('mac_address', '').strip()
        ip_address = request.form.get('ip_address', '').strip()
        port = request.form.get('port', '9')
        notes = request.form.get('notes', '').strip()
        
        # Validation
        if not name or not mac_address:
            flash('Le nom et l\'adresse MAC sont requis.', 'danger')
            return redirect(url_for('add_device'))
        
        # Validate MAC address
        if not validate_mac_address(mac_address):
            flash('Adresse MAC invalide. Format attendu: XX:XX:XX:XX:XX:XX', 'danger')
            return redirect(url_for('add_device'))
        
        # Validate port
        try:
            port = int(port)
            if port < 1 or port > 65535:
                raise ValueError()
        except ValueError:
            flash('Port invalide. Doit être entre 1 et 65535.', 'danger')
            return redirect(url_for('add_device'))
        
        # Default IP if not provided
        if not ip_address:
            ip_address = '255.255.255.255'
        
        # Add device
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO devices (user_id, name, mac_address, ip_address, port, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], name, mac_address, ip_address, port, notes))
        conn.commit()
        conn.close()
        
        flash(f'Appareil "{name}" ajouté avec succès !', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_device.html')

@app.route('/delete-device/<int:device_id>', methods=['POST'])
@login_required
def delete_device(device_id):
    """Delete a device"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM devices WHERE id = ? AND user_id = ?',
                  (device_id, session['user_id']))
    conn.commit()
    conn.close()
    
    flash('Appareil supprimé avec succès.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/wake/<int:device_id>', methods=['POST'])
@login_required
def wake_device(device_id):
    """Send WOL packet to device"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM devices WHERE id = ? AND user_id = ?',
                  (device_id, session['user_id']))
    device = cursor.fetchone()
    conn.close()
    
    if not device:
        return jsonify({'success': False, 'message': 'Appareil non trouvé'}), 404
    
    success, message = send_wol_packet(
        device['mac_address'],
        device['ip_address'] or '255.255.255.255',
        device['port']
    )
    
    return jsonify({'success': success, 'message': message})

@app.route('/help')
def help_page():
    """Help page"""
    return render_template('help.html')

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

if __name__ == '__main__':
    init_db()
    # Debug mode should only be enabled in development
    # Set FLASK_DEBUG=0 in production environment
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 'yes')
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
