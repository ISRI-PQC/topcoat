import random

from .. import params
from .modules import Module


def sample_matrix(ring, rows: int, columns: int) -> Module.Matrix:
    return Module(ring)(
        [
            [ring.random_element(is_ntt=False) for j in range(columns)]
            for i in range(rows)
        ]
    )


def sample_vector_with_max_inf_norm(
    ring, size: int, max_inf_norm: int
) -> Module.Matrix:
    return Module(ring)(
        [
            ring(
                [
                    random.randint(-max_inf_norm, max_inf_norm)
                    for _ in range(params.N)
                ],
                is_ntt=False,
            )
            for _ in range(size)
        ]
    ).transpose_self()


# def inf_norm_of_vector(vector: Module.Matrix):
#     return max(
#         [inf_norm_of_polynomial(poly) for poly in row][0]
#         for row in vector.elements
#     )


# def inf_norm_of_polynomial(poly: PolynomialRing.Polynomial):
#     return max(
#         [abs(centered_modulo(coeff, params.Q)) for coeff in poly.coeffs]
#     )
