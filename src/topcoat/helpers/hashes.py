import hashlib
import itertools
import random

from .. import params
from .polynomials import PolynomialRing


def eval_commitment(commitments: list) -> int:
    data = b"".join([poly.dump() for poly in itertools.chain(*commitments)])
    output = hashlib.shake_256(data).digest(32)
    return int.from_bytes(output, "big")


def hash0(R: PolynomialRing, data: bytes) -> PolynomialRing.Polynomial:
    output = hashlib.shake_256(data).digest(32)
    random.seed(output)
    coeffs = [random.choice([-1, 1]) for _ in range(params.N)]
    dropout_positions = random.sample(range(params.N), params.N - params.TAU)
    for i in dropout_positions:
        coeffs[i] = 0
    random.seed()
    return R(coeffs)


def hash1(data: bytes) -> bytes:
    return hashlib.shake_256(b"hash1" + data).digest(32)


def hash2(data: bytes) -> bytes:
    return hashlib.shake_256(b"hash2" + data).digest(32)


def hash3(data: bytes) -> bytes:
    return hashlib.shake_256(b"hash3" + data).digest(32)


def hash4(data: bytes) -> bytes:
    return hashlib.shake_256(b"hash4" + data).digest(32)
