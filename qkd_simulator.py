from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import os
import random
import hashlib

class LatticeKEM:
    """
    Simulates a Lattice-based Key Encapsulation Mechanism (KEM).
    Based on the 'Learning with Errors' (LWE) problem used in NIST-standard ML-KEM (Kyber).
    """
    def __init__(self, dimension=512):
        self.dimension = dimension
        
    def generate_shared_secret(self):
        """
        Simulates the generation of a Lattice-based shared secret.
        In a real Kyber implementation, this involves:
        1. Public/Private Key generation (Matrix-Vector multiplication with noise).
        2. Encapsulation: Creating a ciphertext with a masked secret.
        3. Decapsulation: Recovering the secret using the private key.
        """
        # We return a 32-byte secret derived from simulated lattice noise
        # This represents the shared secret established via Lattice math.
        return os.urandom(32)

def get_quantum_channel_diagnostics():
    """
    Simulate Quantum Channel Diagnostics (Alice's Side):
    - QBER (Quantum Bit Error Rate): Deviation in polarized photon states.
    - Dark Count Rate: Spontaneous detector clicks without photons.
    - Photonic Pulse Rate: Frequency of photon emission (GHz).
    - Channel stability: Stability of the fiber/free-space link.
    """
    qber = random.uniform(0.01, 0.12)  # Focus on standard QKD operating ranges
    dark_counts = random.uniform(1e-8, 1e-5) # Simulated detector noise
    pulse_rate = random.uniform(0.1, 1.0) # GHz
    stability = random.uniform(0.7, 1.0)
    
    return {
        "qber": qber,
        "dark_counts": dark_counts,
        "pulse_rate": pulse_rate,
        "stability": stability
    }

def select_qkd_protocol(metrics):
    """
    Quantum-Aware Protocol Selection Engine:
    - BB84: Optimal for low-noise high-fidelity fiber links.
    - CASCADE: Enhanced error correction protocol for fluctuating QBER.
    - DPS: Robust for high-loss/ambient-noise environments.
    """
    qber = metrics['qber']
    stability = metrics['stability']
    
    if qber < 0.04 and stability > 0.9:
        return 'BB84'
    elif 0.04 <= qber < 0.08:
        return 'CASCADE'
    else:
        return 'DPS'

def generate_hybrid_quantum_key(protocol):
    """
    Simulates a Hybrid Post-Quantum Key Exchange:
    1. Layer 1 (Physical): QKD-based key generation (Physics-based).
    2. Layer 2 (Mathematical): Lattice-based KEM (Mathematics-based).
    3. Layer 3 (Fusion): Hash-based derivation of the final AES-256 session key.
    """
    # 1. Physics Layer: QKD Secret
    qkd_secret = os.urandom(32) # Simulated photon-derived secret
    
    # 2. Math Layer: Lattice Secret (Simulating Kyber/ML-KEM)
    lattice_kem = LatticeKEM()
    lattice_secret = lattice_kem.generate_shared_secret()
    
    # 3. Hybrid Fusion: Mix both secrets using SHA-256
    # This ensures that even if one layer is compromised, the other remains secure.
    hasher = hashlib.sha256()
    hasher.update(qkd_secret)
    hasher.update(lattice_secret)
    hasher.update(protocol.encode()) # Bind the protocol to the key logic
    
    final_key = hasher.digest() # 256-bit Hybrid Key
    return final_key

def encrypt_data(data_bytes, key):
    """
    Post-Quantum Symmetric Encryption (AES-256-CBC).
    Secures biometric data using the Hybrid Quantum-derived secret key.
    """
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data_bytes) + padder.finalize()
    
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return iv + encrypted_data
