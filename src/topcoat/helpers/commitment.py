import random
from typing import Tuple

from .. import params
from .modules import Module
from .ntt_helper import NTTHelperTopcoat
from .polynomials import PolynomialRing
from .utils import sample_matrix

R = PolynomialRing(
    params.COMMITMENT_Q, params.COMMITMENT_N, ntt_helper=NTTHelperTopcoat
)

M = Module(R)


def commitment_keys(ck: bytes) -> Tuple[Module.Matrix, Module.Matrix]:
    random.seed(ck)
    A1_prime = sample_matrix(
        R, params.COMMITMENT_n, params.COMMITMENT_K - params.COMMITMENT_n
    )
    A1 = M.eye(params.COMMITMENT_n) | A1_prime

    A2_prime = sample_matrix(
        R,
        params.COMMITMENT_L,
        params.COMMITMENT_K - params.COMMITMENT_L - params.COMMITMENT_n,
    )

    A2 = (
        M.zeros(params.COMMITMENT_L, params.COMMITMENT_n)
        | M.eye(params.COMMITMENT_L)
        | A2_prime
    )

    random.seed()

    return A1, A2


def commit(
    A1: Module.Matrix, A2: Module.Matrix, m: Module.Matrix, r: Module.Matrix
) -> Tuple[Module.Matrix, Module.Matrix]:
    c1 = A1 @ r
    c2 = A2 @ r + m
    return c1, c2


def open_commitment(
    A1: Module.Matrix,
    A2: Module.Matrix,
    c1: Module.Matrix,
    c2: Module.Matrix,
    m: Module.Matrix,
    r: Module.Matrix,
) -> bool:
    c1_result = A1 @ r
    c2_result = A2 @ r + m

    return (
        c1_result == c1
        and c2_result == c2
        and m.second_norm() <= params.COMMITMENT_BETA
    )
