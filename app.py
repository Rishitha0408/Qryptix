from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import io
import zipfile
import base64
from datetime import datetime
from functools import wraps
import logging

from models import db, User, Folder, MedicalImage
from qkd_simulator import get_quantum_channel_diagnostics, select_qkd_protocol, generate_quantum_key, encrypt_data

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'SuperSecretKey_QKD_PQE_Qryptix_2026'

# Rate Limiting Configuration
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Admin Audit Logging Configuration
if os.environ.get('VERCEL') == '1':
    # On Vercel, log to stdout/stderr (standard practice)
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    print("Vercel environment detected. Logging to console.")
else:
    # Local development: keep file logging
    logging.basicConfig(filename='admin_approvals.log', level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')

# --- Permanent Postgres Configuration for Vercel ---
if os.environ.get('VERCEL') == '1':
    # Vercel provides POSTGRES_URL or DATABASE_URL when you connect Neon/Postgres
    database_url = os.environ.get('POSTGRES_URL') or os.environ.get('DATABASE_URL')
    
    if database_url:
        # SQLAlchemy requires 'postgresql://' but Vercel sometimes provides 'postgres://'
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Emergency fallback to /tmp if Postgres is not found but running on Vercel
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/database_v2.db'
else:
    # Standard SQLite for Local Development
    db_path = os.path.join(basedir, 'instance', 'database_v2.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '/tmp/uploads' if os.environ.get('VERCEL') else os.path.join(basedir, 'uploads')
app.config['SECURE_FOLDERS'] = '/tmp/secure_folders' if os.environ.get('VERCEL') else os.path.join(basedir, 'secure_folders')

print(f"Database located at: {app.config['SQLALCHEMY_DATABASE_URI']}")

db.init_app(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SECURE_FOLDERS'], exist_ok=True)

with app.app_context():
    try:
        db.create_all()
        
        # Auto-migration: Ensure state_medical_council column exists (Helps with Vercel/Neon deployment)
        try:
            from sqlalchemy import text
            db.session.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS state_medical_council VARCHAR(100)'))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            # Fallback for SQLite which doesn't support 'IF NOT EXISTS' in ALTER TABLE
            try:
                db.session.execute(text('ALTER TABLE "user" ADD COLUMN state_medical_council VARCHAR(100)'))
                db.session.commit()
            except:
                db.session.rollback()

        # Create an admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            hashed_password = generate_password_hash('admin123')
            admin_user = User(username='admin', email='admin@qryptix.com', password=hashed_password, role='admin', is_approved=True, is_license_valid=True)
            db.session.add(admin_user)
            db.session.commit()
    except Exception as startup_err:
        print(f"CRITICAL: Startup database error: {startup_err}")
        # We don't crash the whole app here so the user can at least see a 500 error or similar instead of a hard crash

# --- Context Processor ---
@app.context_processor
def inject_user():
    user = None
    try:
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
    except Exception as e:
        print(f"Context Processor Error: {e}")
    return dict(user=user)

@app.route('/health')
def health():
    return "Qryptix Portal Status: ONLINE", 200

# --- Decorators for Standard Session Authorization ---
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("System authentication required.", "danger")
            return redirect(url_for('login'))
        current_user = User.query.get(session['user_id'])
        if not current_user:
            session.pop('user_id', None)
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

def mock_govt_verification(license_id):
    if license_id and len(license_id) >= 8:
        return True
    return False

@app.errorhandler(500)
def internal_error(error):
    import traceback
    return f"<h1>Internal Server Error (500)</h1><p>Detailed Error: {error}</p><pre>{traceback.format_exc()}</pre>", 500

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        mobile_number = request.form.get('mobile_number')
        registration_year = request.form.get('registration_year')
        state_medical_council = request.form.get('state_medical_council')
        password = request.form.get('password')
        license_id = request.form.get('license_id')

        if User.query.filter_by(username=username).first():
            flash("Username already exists in Qryptix registry.", "danger")
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash("Email already registered in Qryptix.", "danger")
            return redirect(url_for('register'))

        if User.query.filter_by(license_id=license_id).first():
            flash("License ID already registered for another member.", "danger")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            full_name=full_name,
            email=email,
            mobile_number=mobile_number,
            registration_year=registration_year,
            state_medical_council=state_medical_council,
            password=hashed_password,
            license_id=license_id,
            role='doctor',
            is_license_valid=False,
            is_approved=False
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Qryptix registration successful! System stored as unverified + unapproved. Portal access pending admin clearance.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            if user.role == 'doctor':
                if not user.is_license_valid or not user.is_approved:
                    flash("Access Denied: Your medical license is either unverified or pending Qryptix clearance.", "warning")
                    return redirect(url_for('login'))
                
            session['user_id'] = user.id
            flash(f"Welcome back to Qryptix Retinal Vault, {user.username}.", "success")
            
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('doctor_dashboard'))
        else:
            flash("Invalid credentials or unauthorized access.", "danger")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))

@app.route('/admin_dashboard')
@login_required
@admin_required
def admin_dashboard(current_user):
    pending_doctors = User.query.filter_by(role='doctor').filter((User.is_approved == False) | (User.is_license_valid == False)).all()
    approved_doctors = User.query.filter_by(role='doctor', is_approved=True, is_license_valid=True).all()
    return render_template('admin_dashboard.html', user=current_user, pending=pending_doctors, approved=approved_doctors)

@app.route('/verify-license/<int:user_id>')
@login_required
@admin_required
def verify_license(current_user, user_id):
    user = User.query.get_or_404(user_id)
    user.is_license_valid = True
    db.session.commit()
    logging.info(f"Admin {current_user.username} verified license for Doctor {user.username} (License ID: {user.license_id})")
    flash(f"Medical License for '{user.username}' marked as VALID.", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/approve/<int:user_id>')
@login_required
@admin_required
def approve_doctor(current_user, user_id):
    user = User.query.get_or_404(user_id)
    if not user.is_license_valid:
        flash(f"Cannot approve '{user.username}' until license is verified.", "warning")
        return redirect(url_for('admin_dashboard'))
    
    user.is_approved = True
    db.session.commit()
    logging.info(f"Admin {current_user.username} approved Doctor {user.username}")
    flash(f"Doctor '{user.username}' clearance approved. Access granted.", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/reject/<int:user_id>')
@login_required
@admin_required
def reject_doctor(current_user, user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash("Cannot reject an administrator.", "danger")
        return redirect(url_for('admin_dashboard'))
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f"Doctor '{username}' request rejected and removed.", "warning")
    return redirect(url_for('admin_dashboard'))

@app.route('/doctor_dashboard')
@login_required
def doctor_dashboard(current_user):
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    folders = Folder.query.filter_by(user_id=current_user.id).all()
    return render_template('doctor_dashboard.html', user=current_user, folders=folders)

@app.route('/create_folder', methods=['POST'])
@login_required
def create_folder(current_user):
    name = request.form.get('folder_name')
    if not name:
        flash("Folder name is required.", "danger")
        return redirect(url_for('doctor_dashboard'))
        
    new_folder = Folder(name=name, user_id=current_user.id)
    db.session.add(new_folder)
    db.session.commit()
    
    folder_path = os.path.join(app.config['SECURE_FOLDERS'], str(new_folder.id))
    os.makedirs(folder_path, exist_ok=True)
    
    flash(f"Workspace '{name}' created successfully.", "success")
    return redirect(url_for('doctor_dashboard'))

@app.route('/folder/<int:folder_id>', methods=['GET'])
@login_required
def folder_view(current_user, folder_id):
    folder = Folder.query.get_or_404(folder_id)
    if folder.user_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('doctor_dashboard'))
        
    images = MedicalImage.query.filter_by(folder_id=folder.id).all()
    return render_template('folder_view.html', user=current_user, folder=folder, images=images)

def doctor_required(f):
    @wraps(f)
    def decorated_function(current_user, *args, **kwargs):
        if current_user.role != 'doctor':
            flash("Doctor access required.", "danger")
            return redirect(url_for('admin_dashboard'))
        return f(current_user, *args, **kwargs)
    return decorated_function

@app.route('/upload-images/<int:folder_id>', methods=['POST'])
@login_required
@doctor_required
def upload_images(current_user, folder_id):
    folder = Folder.query.get_or_404(folder_id)
    if folder.user_id != current_user.id:
        flash("Unauthorized access to workspace.", "danger")
        return redirect(url_for('doctor_dashboard'))

    files = request.files.getlist('images')
    if not files or all(f.filename == '' for f in files):
        flash("No retinal data selected for encryption.", "danger")
        return redirect(url_for('folder_view', folder_id=folder_id))

    upload_stats = {'BB84': 0, 'CASCADE': 0, 'DPS': 0}
    successful = 0
    folder_dir = os.path.join(app.config['SECURE_FOLDERS'], str(folder.id))
    os.makedirs(folder_dir, exist_ok=True)

    for file in files:
        if file and file.filename:
            # When folders are uploaded, browsers send relative paths. Extract valid file extensions only.
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tif', '.tiff', '.webp', '.dcm', '.dicom']:
                continue
                
            filename = secure_filename(os.path.basename(file.filename))
            file_data = file.read()
            
            metrics = get_quantum_channel_diagnostics()
            protocol = select_qkd_protocol(metrics)
            if 'BB84' in protocol: upload_stats['BB84'] += 1
            if 'CASCADE' in protocol: upload_stats['CASCADE'] += 1
            if 'DPS' in protocol: upload_stats['DPS'] += 1
            
            key = generate_quantum_key(protocol)
            encrypted_data = encrypt_data(file_data, key)
            
            base_name, _ = os.path.splitext(filename)
            enc_filename = f"{base_name}_encrypted.bin"
            key_filename = f"{base_name}_secret_key.bin"
            
            enc_path = os.path.join(folder_dir, enc_filename)
            key_path = os.path.join(folder_dir, key_filename)
            
            with open(enc_path, 'wb') as f: f.write(encrypted_data)
            with open(key_path, 'wb') as f: f.write(key)
                
            new_image = MedicalImage(
                folder_id=folder.id,
                original_filename=file.filename,
                encrypted_image_path=enc_path,
                key_path=key_path,
                qkd_protocol_used=protocol
            )
            db.session.add(new_image)
            successful += 1
            
    db.session.commit()
    if successful > 0:
        flash(f"Quantum Sequence Complete. {successful} retinal images secured via Purely Quantum Cryptography. Protocols used: BB84({upload_stats['BB84']}), CASCADE({upload_stats['CASCADE']}), DPS({upload_stats['DPS']})", "success")
    else:
        flash("No valid medical images were found in the selection.", "warning")
    return redirect(url_for('folder_view', folder_id=folder_id))

@app.route('/deactivate-folder/<int:folder_id>')
@login_required
@doctor_required
def deactivate_folder(current_user, folder_id):
    folder = Folder.query.get_or_404(folder_id)
    if folder.user_id != current_user.id:
        flash("Unauthorized command.", "danger")
        return redirect(url_for('doctor_dashboard'))
    folder.is_active = False
    db.session.commit()
    flash(f"Workspace '{folder.name}' deactivated and moved to archive.", "info")
    return redirect(url_for('doctor_dashboard'))

@app.route('/activate-folder/<int:folder_id>')
@login_required
@doctor_required
def activate_folder(current_user, folder_id):
    folder = Folder.query.get_or_404(folder_id)
    if folder.user_id != current_user.id:
        flash("Unauthorized command.", "danger")
        return redirect(url_for('doctor_dashboard'))
    folder.is_active = True
    db.session.commit()
    flash(f"Workspace '{folder.name}' reactivated.", "success")
    return redirect(url_for('doctor_dashboard'))

@app.route('/download/encrypted/<int:image_id>')
@login_required
def download_encrypted(current_user, image_id):
    image = MedicalImage.query.get_or_404(image_id)
    if image.folder.user_id != current_user.id:
        return "Unauthorized", 403
    return send_file(image.encrypted_image_path, as_attachment=True)

@app.route('/download/key/<int:image_id>')
@login_required
def download_key(current_user, image_id):
    image = MedicalImage.query.get_or_404(image_id)
    if image.folder.user_id != current_user.id:
        return "Unauthorized", 403
    return send_file(image.key_path, as_attachment=True, download_name=os.path.basename(image.key_path))

@app.route('/folder/<int:folder_id>/download_zip')
@login_required
def download_folder_zip(current_user, folder_id):
    folder = Folder.query.get_or_404(folder_id)
    if folder.user_id != current_user.id:
        return "Unauthorized", 403

    images = MedicalImage.query.filter_by(folder_id=folder.id).all()
    if not images:
        flash("No files available to download.", "warning")
        return redirect(url_for('folder_view', folder_id=folder.id))

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for img in images:
            if os.path.exists(img.encrypted_image_path):
                zf.write(img.encrypted_image_path, os.path.basename(img.encrypted_image_path))
            if os.path.exists(img.key_path):
                zf.write(img.key_path, os.path.basename(img.key_path))
                
    memory_file.seek(0)
    return send_file(memory_file, download_name=f"Workspace_{folder.name}_Encrypted_Data.zip", as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
