# Qryptix: Quantum-Secured Retinal Biometric Vault

### About
Traditional medical databases store sensitive retinal biometrics using encryption (RSA/ECC) that is vulnerable to future quantum computing strikes, leading to permanent identity theft. This project builds a **Quantum-Secured Medical Data Vault**—a Flask-based secure portal that:
- **Simulates QKD Protocols**: Generates future-proof keys using BB84, CASCADE, and DPS.
- **Purely Quantum Cryptography**: Encrypts and secures biometric images via **AES-256**.
- **Official Physician Verification**: Mandatory manual check against the **National Medical Commission (NMC)** registry before granting access.

## 🚀 Key Features

### 1. Quantum Key Distribution (QKD) Simulation
Securely encrypts patient data using simulated quantum channels. The system dynamically selects protocols based on channel diagnostics:
- **BB84**: Basic quantum key distribution.
- **CASCADE**: Error-correction focused protocol.
- **DPS (Differential Phase Shift)**: High-speed authentication and encryption.

### 2. Dual-Layer Encryption
- **Asymmetric**: Quantum keys are generated for secure handshake simulations.
- **Symmetric**: Final data encryption via **AES-256** to ensure zero-knowledge storage.

### 3. Healthcare Provider Verification (NMC-Portal Integrated)
A multi-stage registration process to prevent unauthorized access:
- **Doctor Registration**: Mandatory submission of National Medical License IDs.
- **Manual Verification**: Admin integration with the **National Medical Commission (NMC)** IMR registry.
- **Conditional Access**: Accounts are locked as "Unverified + Unapproved" until a manual valid-status check is performed.

### 4. Advanced Security Suite
- **Password Hashing**: Industry-standard `werkzeug.security` implementation.
- **Login Rate Limiting**: Built-in protection against brute-force attacks via `Flask-Limiter`.
- **Audit Logging**: Comprehensive logs for all administrative approvals and license verifications.

## 🛠️ Technology Stack
- **Backend**: Python / Flask
- **Database**: SQLite (Local) / PostgreSQL (Production)
- **Security**: Werkzeug, Cryptography, Flask-Limiter
- **Frontend**: HTML5, Vanilla CSS (Glassmorphism UI), FontAwesome
- **Deployment**: Render / PythonAnywhere / Railway

## 📦 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/qryptix-vault.git
   cd qryptix-vault
   ```

2. **Set up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Locally**:
   ```bash
   python app.py
   ```
   Access the portal at `http://127.0.0.1:5000`.

## 🌐 Deployment (Recommended Alternatives)

Due to recent infrastructure shifts, we recommend the following platforms for hosting:

### 1. Render (Web Services)
- **Setup**: Create a new Web Service and link this GitHub repository.
- **Start Command**: `gunicorn app:app`
- **Environment**: Set `DATABASE_URL` if using an external PostgreSQL instance.

### 2. PythonAnywhere
- **Setup**: Perfect for simple Flask hosting.
- **Note**: Ensure you configure the VirtualEnv and set the paths in the `WSGI configuration` file.

### 3. Railway
- **Setup**: High-performance hosting with easy environment variable management.

---
*Disclaimer: This prototype is intended for research and hackathon purposes. The quantum protocols are simulated to demonstrate the architectural implementation of future-proof medical data storage.*
