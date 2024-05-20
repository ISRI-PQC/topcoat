import logging

PARALLEL_SESSIONS = 5  # How many commitments to do in parallel
LOGGING_LEVEL = logging.DEBUG

# All parameters are based/inspired by NIST Level 2 Dilithium
N = 256
Q = 8380417
Q_INV = 58728449  # multiplicative inverse of q modulo 2^32

D = 13  # Number of bits dropped from t
K = 4  # Matrices size
L = 4
# L = 3
ETA = 2  # Secret distribution
TAU = 39  # Number of +- in hash challenge
BETA = 78  # The maximum coefficient in cs
GAMMA = 131072  # Rejection sampling 2^{17}
# GAMMA = 524288 #2^{19}
GAMMA_PRIME = 95232  # // 2  # (q − 1)/88 / 2
# GAMMA_PRIME = 261888 # (q − 1)/32

CRHBYTES = 48
SEEDBYTES = 32

# Commitment parameters
COMMITMENT_Q = 8380417
COMMITMENT_N = 256  # maximum order
COMMITMENT_K = 15
COMMITMENT_L = K
COMMITMENT_n = 5
COMMITMENT_D = 2
COMMITMENT_BETA = 256
