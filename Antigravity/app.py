from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
import io
import zipfile
import jwt
from datetime import datetime, timedelta
from functools import wraps

from models import db, User, Folder, MedicalImage
from qkd_simulator import get_channel_metrics, select_qkd_protocol, generate_quantum_key, encrypt_data, decrypt_data

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SuperSecretKey_QKD_PQE_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
app.config['SECURE_FOLDERS'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'secure_folders')

db.init_app(app)
bcrypt = Bcrypt(app)

# Ensure upload/secure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SECURE_FOLDERS'], exist_ok=True)

# Application Context initialization
with app.app_context():
    db.create_all()
    # Create an admin user if it doesn't exist
    if not User.query.filter_by(username='admin').first():
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin_user = User(username='admin', password=hashed_password, role='admin', is_approved=True)
        db.session.add(admin_user)
        db.session.commit()

# --- Decorator for JWT Session Validation ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = session.get('token')
        if not token:
            flash("Please log in to access this page.", "danger")
            return redirect(url_for('login'))
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            flash("Token is invalid or expired! Please login again.", "danger")
            session.pop('token', None)
            return redirect(url_for('login'))
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            flash("Administrator access required.", "danger")
            return redirect(url_for('doctor_dashboard'))
        return f(current_user, *args, **kwargs)
    return decorated

# Mock Government Database Check
def mock_govt_verification(license_id):
    # Imagine an external API call here
    if license_id and license_id.startswith('GOV-') and len(license_id) >= 8:
        return True
    return False

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        license_id = request.form.get('license_id')

        # Check existing user
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for('register'))

        # Govt License Verification
        if not mock_govt_verification(license_id):
            flash("Invalid License ID. Government verification failed.", "danger")
            return redirect(url_for('register'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            username=username,
            password=hashed_password,
            license_id=license_id,
            role='doctor',
            is_approved=False # needs admin approval
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Pending Admin Approval.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            if not user.is_approved:
                flash("Account pending admin approval.", "warning")
                return redirect(url_for('login'))
                
            token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            
            session['token'] = token
            flash("Login successful!", "success")
            
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('doctor_dashboard'))
        else:
            flash("Invalid credentials.", "danger")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('token', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))

@app.route('/admin_dashboard')
@token_required
@admin_required
def admin_dashboard(current_user):
    pending_doctors = User.query.filter_by(role='doctor', is_approved=False).all()
    approved_doctors = User.query.filter_by(role='doctor', is_approved=True).all()
    return render_template('admin_dashboard.html', user=current_user, pending=pending_doctors, approved=approved_doctors)

@app.route('/approve/<int:user_id>')
@token_required
@admin_required
def approve_doctor(current_user, user_id):
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    flash(f"Doctor '{user.username}' approved.", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/doctor_dashboard')
@token_required
def doctor_dashboard(current_user):
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    folders = Folder.query.filter_by(user_id=current_user.id).all()
    return render_template('doctor_dashboard.html', user=current_user, folders=folders)

@app.route('/create_folder', methods=['POST'])
@token_required
def create_folder(current_user):
    name = request.form.get('folder_name')
    folder_password = request.form.get('folder_password')
    
    if not name or not folder_password:
        flash("Name and password are required.", "danger")
        return redirect(url_for('doctor_dashboard'))
        
    hashed_pwd = bcrypt.generate_password_hash(folder_password).decode('utf-8')
    new_folder = Folder(name=name, user_id=current_user.id, hashed_password=hashed_pwd)
    db.session.add(new_folder)
    db.session.commit()
    
    # Create actual directory
    folder_path = os.path.join(app.config['SECURE_FOLDERS'], str(new_folder.id))
    os.makedirs(folder_path, exist_ok=True)
    
    flash(f"Secure folder '{name}' created.", "success")
    return redirect(url_for('doctor_dashboard'))

@app.route('/verify_folder_access/<int:folder_id>', methods=['POST'])
@token_required
def verify_folder_access(current_user, folder_id):
    folder = Folder.query.get_or_404(folder_id)
    if folder.user_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('doctor_dashboard'))
        
    pwd = request.form.get('folder_password')
    if bcrypt.check_password_hash(folder.hashed_password, pwd):
        # Set a temporary session flag for folder open
        session[f'unlocked_folder_{folder.id}'] = True
        return redirect(url_for('folder_view', folder_id=folder.id))
    else:
        flash("Incorrect folder password.", "danger")
        return redirect(url_for('doctor_dashboard'))

@app.route('/folder/<int:folder_id>', methods=['GET'])
@token_required
def folder_view(current_user, folder_id):
    folder = Folder.query.get_or_404(folder_id)
    if folder.user_id != current_user.id or not session.get(f'unlocked_folder_{folder.id}'):
        flash("Please unlock the folder first.", "warning")
        return redirect(url_for('doctor_dashboard'))
        
    images = MedicalImage.query.filter_by(folder_id=folder.id).all()
    return render_template('folder_view.html', user=current_user, folder=folder, images=images)

@app.route('/folder/<int:folder_id>/upload', methods=['POST'])
@token_required
def upload_images(current_user, folder_id):
    folder = Folder.query.get_or_404(folder_id)
    if folder.user_id != current_user.id or not session.get(f'unlocked_folder_{folder.id}'):
        flash("Unauthorized.", "danger")
        return redirect(url_for('doctor_dashboard'))

    files = request.files.getlist('images')
    if not files or files[0].filename == '':
        flash("No selected file", "danger")
        return redirect(url_for('folder_view', folder_id=folder.id))

    upload_stats = {'BB84': 0, 'CASCADE': 0, 'DPS': 0}
    
    folder_dir = os.path.join(app.config['SECURE_FOLDERS'], str(folder.id))

    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            # Read file data
            file_data = file.read()
            
            # Dynamic QKD metrics & selection
            qber, stability = get_channel_metrics()
            protocol = select_qkd_protocol(qber, stability)
            upload_stats[protocol] += 1
            
            # Generate key and encrypt
            key = generate_quantum_key(protocol)
            encrypted_data = encrypt_data(file_data, key)
            
            base_name, _ = os.path.splitext(filename)
            enc_filename = f"{base_name}_enc.bin"
            key_filename = f"{base_name}_key.key"
            
            enc_path = os.path.join(folder_dir, enc_filename)
            key_path = os.path.join(folder_dir, key_filename)
            
            # Write encrypted data and key to file system
            with open(enc_path, 'wb') as f:
                f.write(encrypted_data)
            with open(key_path, 'wb') as f:
                f.write(key)
                
            # Database entry
            new_image = MedicalImage(
                folder_id=folder.id,
                original_filename=filename,
                encrypted_image_path=enc_path,
                key_path=key_path,
                qkd_protocol_used=protocol
            )
            db.session.add(new_image)
            
    db.session.commit()
    flash(f"Successfully encrypted and uploaded {len(files)} files. QKD Stats: BB84({upload_stats['BB84']}), CASCADE({upload_stats['CASCADE']}), DPS({upload_stats['DPS']})", "success")
    return redirect(url_for('folder_view', folder_id=folder.id))

@app.route('/folder/<int:folder_id>/download/<int:image_id>')
@token_required
def download_image(current_user, folder_id, image_id):
    folder = Folder.query.get_or_404(folder_id)
    if folder.user_id != current_user.id or not session.get(f'unlocked_folder_{folder.id}'):
        return "Unauthorized", 403
        
    image = MedicalImage.query.get_or_404(image_id)
    if image.folder_id != folder.id:
        return "Image not found in folder", 404
        
    # Read encrypted data and key
    with open(image.encrypted_image_path, 'rb') as f:
        encrypted_data = f.read()
    with open(image.key_path, 'rb') as f:
        key = f.read()
        
    decrypted_data = decrypt_data(encrypted_data, key)
    
    # Return as file stream
    return send_file(
        io.BytesIO(decrypted_data),
        download_name=image.original_filename,
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
