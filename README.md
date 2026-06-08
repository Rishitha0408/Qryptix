# Qryptix: Quantum-Secured Retinal Biometric Vault

### About
Traditional medical databases store sensitive retinal biometrics using encryption (RSA/ECC) that is vulnerable to future quantum computing strikes, leading to permanent identity theft. **Qryptix** is a high-performance, quantum-secured medical data vault built in Flask. It integrates physical-layer **Quantum Key Distribution (QKD) Simulations** with mathematical-layer **Lattice-Based Key Encapsulation Mechanisms (KEM)** to encrypt and secure medical images using **AES-256-CBC**.

In addition, Qryptix implements strict physician verification aligned with the **National Medical Commission (NMC)** registry database, safeguarding medical biometrics from unauthorized access.

---

## 🚀 Key Features

### 1. Quantum Key Distribution (QKD) Simulation
The system monitors channel diagnostics in real-time to select the optimal QKD protocol:
- **BB84 (Standard Polarization Key Exchange)**: Selected when channel noise is low (QBER < 4%) and stability is high (> 90%). Offers the fastest photon polarization key rates.
- **CASCADE (Error-Correction Mode)**: Selected under moderate noise (QBER between 4% and 8%). Performs iterative bit-level parity reconciliation to guarantee 100% key agreement.
- **DPS (Differential Phase Shift)**: Selected when channel noise is high (QBER >= 8%) or stability is low (<= 90%). Encodes phase-shifted pulses for maximum resilience to environmental interference.

### 2. Hybrid Post-Quantum Key Exchange
For every image upload, a multi-layer hybrid key is generated:
1. **Physical Layer**: Key generated via the selected QKD protocol simulation.
2. **Mathematical Layer (Lattice-Based)**: Shared secret derived from learning-with-errors (LWE) noise parameters simulating ML-KEM/Kyber.
3. **Hybrid Fusion**: Both keys and the selected protocol identifier are combined using **SHA-256** to construct a final 256-bit symmetric session key. Even if one mathematical or physical layer is compromised, the other retains complete cryptographic integrity.

### 3. Symmetric Grover's & Shor's Resistance
- **Shor's Algorithm Immunity**: Being a purely symmetric vault (using AES-256 for biometric storage), Qryptix is immune to Shor's algorithm, which only targets asymmetric prime factorization/discrete logarithms.
- **Grover's Algorithm Defense**: By utilizing **256-bit keys**, the vault maintains a solid 128-bit post-quantum security floor against Grover's square-root search optimization.

### 4. Healthcare Provider Verification (NMC-Portal)
- **Doctor Registration**: Mandatory input of name, registration year, state medical council, and license ID.
- **Cross-Attribute Verification**: The system cross-references submitted details against official National Medical Commission (NMC) IMR records stored in the verification database, validating spelling, year, and state.
- **Administrative Clearance**: Accounts remain locked as "Unverified" and "Unapproved" until manually verified by an administrator.

### 5. Advanced Security Controls
- **Password Hashing**: Securely managed using `werkzeug.security`.
- **Login Rate Limiting**: Managed by `Flask-Limiter` to mitigate brute-force attempts.
- **Detailed Audit Logging**: Logs registration, manual admin verifications, and approvals to `admin_approvals.log`.

---

## 🛠️ Technology Stack
- **Backend**: Python / Flask
- **Database**: SQLite (Local, auto-migrated on startup) / PostgreSQL (Production)
- **Security**: Cryptography (PyCA), Werkzeug, Flask-Limiter
- **Frontend**: HTML5, Vanilla CSS (Premium Glassmorphism Design), FontAwesome
- **Data Sync**: openpyxl (for importing official NMC physician registers)

---

## 📦 Local Installation & Running

### 1. Set Up the Environment
Clone the repository and navigate to the project directory:
```bash
git clone https://github.com/your-username/qryptix-vault.git
cd qryptix-vault
```

Set up and activate a Python virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install requirements:
```bash
pip install -r requirements.txt
```

### 2. Run the Application
Start the Flask web server:
```bash
python app.py
```
The application will boot up at **`http://127.0.0.1:5000`**.

---

## 🔑 Administrative & Diagnostic Workflows

### Default Admin Account
To manage approvals and verification, log in as administrator using:
- **Username**: `admin`
- **Password**: `admin123`

Once logged in, navigate to the **Admin Dashboard** to inspect pending registrations and synchronize NMC datasets.

### Utility & Verification Scripts
The repository contains several scripts for developer diagnostics and database management:
- **[manual_import.py](file:///c:/Users/madha/.gemini/antigravity/playground/inertial-apogee/manual_import.py)**: Imports the official registry of physicians from `dummy_doctors_updated (2).xlsx` into the SQLite database.
- **[test_modules_tmp.py](file:///c:/Users/madha/.gemini/antigravity/playground/inertial-apogee/test_modules_tmp.py)**: Performs verification of Python dependency imports, tests local database connectivity, and runs simulated QKD channel diagnostic sweeps.
- **Swathi Verification Scripts** (`check_swathi_v4.py`, `force_validate_swathi.py`): Test registration integrity and validation flows for the placeholder doctor account `swathi`.

---

*Disclaimer: This prototype is intended for research and hackathon purposes. The quantum protocols are simulated to demonstrate the architectural implementation of future-proof medical data storage.*
