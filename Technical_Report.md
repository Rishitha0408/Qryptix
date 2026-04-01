# Qryptix: Purely Quantum Cryptography Retinal Vault
## Technical Implementation Report

### 1. Executive Summary
**Qryptix** is a high-performance specialized medical archive engineered exclusively for the secure storage of **Retinal Biometric Data**. The system utilizes **Purely Quantum Cryptography**—integrating simulated Quantum Key Distribution (QKD) channels with 256-bit symmetric encryption to ensure immunity against the fastest evolving quantum-computing threats.

### 2. Hybrid Quantum Security Core
The security of **Qryptix** is built on a dual-layered defense combining quantum physics and post-quantum mathematics:
*   **Layer 1: Quantum Key Distribution (QKD)**: Qryptix simulates a physical photonic link to establish keys based on the laws of physics (no-cloning theorem).
*   **Layer 2: Lattice-Based KEM (ML-KEM/Kyber)**: Even if the quantum channel is bypassed, the system uses Lattice-based mathematics (Shortest Vector Problem) which is mathematically resistant to quantum factoring.
*   **Symmetric Post-Quantum Logic**: The final **Hybrid Key** is used with **AES-256**, ensuring the data remains secure against both Shor's and Grover's algorithms.

### 3. Quantum Resistance: Shor's and Grover's
*   **Shor's Algorithm Immunity**: As a purely symmetric system, Qryptix is mathematically immune to Shor’s algorithm, which only targets asymmetric factorization problems.
*   **Grover's Algorithm Defense**: By doubling the standard key length to **256 bits**, the system maintains a 128-bit security floor against Grover’s square-root search speedup.

### 4. Specialized Purpose: Retinal Biometrics
Qryptix is optimized specifically for **Retinal Images**. This specialization allows for:
*   Standardized binary processing for high-resolution retinal scans.
*   Secure archival of diagnostic eye data for long-term health monitoring.
*   Protected medical workflows tailored for ophthalmology departments.

### 5. Advanced QKD Protocol Selection Engine
The system features a **Quantum-Aware Protocol Engine** that dynamically analyzes the state of the photonic channel before each encryption operation.

#### 5.1 When are Protocols Selected?
The selection occurs in **Real-Time** during the upload phase of each retinal image. For every individual file received, the system probes the simulated quantum channel to generate a set of diagnostics: **QBER (Quantum Bit Error Rate)** and **Channel Stability**.

#### 5.2 Selection Logic and Purpose of Protocols:

##### 1. BB84 (Standard Polarization Key Exchange)
*   **Selection Criteria**: QBER < 0.04 and Stability > 0.9.
*   **Purpose**: BB84 is the gold standard for **High-Efficiency Transmission**. When the fiber-optic channel is clear and noise is minimal, BB84 provides the fastest key generation rate using rectilinear and diagonal photon polarization bases.

##### 2. CASCADE (Error-Correction Focused Mode)
*   **Selection Criteria**: 0.04 <= QBER < 0.08.
*   **Purpose**: This mode focuses on **Information Reconciliation**. When moderate noise is detected, the system prioritizes bit-level parity checking. CASCADE uses an iterative process to find and fix errors, ensuring that 100% data integrity is maintained even when the photonic link fluctuates.

##### 3. DPS (Differential Phase Shift)
*   **Selection Criteria**: QBER >= 0.08 or Stability <= 0.9.
*   **Purpose**: DPS is a **Noise-Resilient Mode**. Instead of using polarization (which can be easily disturbed), DPS encodes information in the relative phase of consecutive photon pulses. This makes it ideal for protecting retinal images over long distances or through unstable free-space links where standard QKD might fail.

### 6. System Workflow and Processing Model
The application follows a defined end-to-end security workflow tailored for the medical environment:

#### 6.1 Step 1: Identity & Clearance
*   **Physician Registration**: Doctors must register with a valid Government License ID.
*   **Admin Approval**: Access is non-immediate; an administrator must verify and approve the doctor’s credentials.

#### 6.2 Step 2: Workspace Isolation
*   Isolated "Workspaces" for each patient case ensure metadata and storage are strictly partitioned by physician ownership.

#### 6.3 Step 3: Biometric Upload and Hybrid Sifting
*   **Upload Mechanism**: Supports both individual image selection and **Bulk Folder Uploads**.
*   **Quantum Diagnostics**: For each file, the system triggers the **Quantum Channel Diagnostic Hub** to choose the best protocol (BB84, CASCADE, or DPS).
*   **Lattice Encapsulation**: Simultaneously, a lattice-based shared secret is generated.
*   **Key Fusion**: The QKD secret and Lattice secret are fused using SHA-256 to create the final 256-bit session key.

#### 6.4 Step 4: Final Archival
*   After the hybrid key generation, the retinal data is encrypted with **AES-256-CBC** and saved to the storage layer.

### 7. Data Storage and Database Retrieval

#### 7.1 Storage Architecture
*   **Physical Layer**: Encrypted retinal images are stored as `.bin` binary files in `/secure_folders/{workspace_id}/`.
*   **Key Layer**: Quantum Secret Keys are exported as independent `.bin` files for the doctor.

#### 7.2 Database and Retrieval Logic
QuantiBio Shield manages metadata using an **SQLAlchemy-based SQLite database** (`database_v2.db`) to track file paths, original filenames, and the specific **QKD Protocol** assigned to each retinal image.

### 8. System Limitations
*   **Simulation vs. Hardware**: The quantum channel (QBER, Pulsing) is currently simulated in Python.
*   **Key Recovery**: No "Central Key Master" exists; loss of the secret key `.bin` results in permanent data loss.
*   **Database Security**: Metadata is stored in standard plaintext within the SQLite system.

### 9. Conclusion
**Qryptix** demonstrates how purely quantum concepts can be practicalized for the most sensitive medical data. By focusing specifically on retinal biometrics and utilizing a dual-layered storage and database retrieval model, it provides a state-of-the-art framework for future-proof medical record management.
