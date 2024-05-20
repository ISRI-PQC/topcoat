from typing import Tuple

from .modules import Module
from .polyutils import centered_modulo


def hint(
    r: Module.Matrix, r_prime: Module.Matrix, alpha: int
) -> Tuple[Module.Matrix, Module.Matrix]:
    # Version with pure alpha, without q-1 - WORKING
    # ====== STEP 1 ======
    h = r.sub(r_prime, False)
    # h.apply_to_every_coeff(centered_modulo) - with this, h1 is always zero

    divisor = alpha

    # ====== STEP 3 ======
    h2 = h.copy()
    h2.apply_to_every_coeff(lambda x: centered_modulo(x, divisor))

    # ====== STEP 2 ======
    h1 = h.sub(h2, False)
    h1.apply_to_every_coeff(lambda x: x // divisor)

    # # Paper version with Peeter's trick to calculate h2 first
    # # ====== STEP 1 ======
    # h = r - r_prime
    # # h.apply_to_every_coeff(centered_modulo) - with this, h1 is always zero

    # divisor = (params.Q - 1) // alpha

    # # ====== STEP 3 ======
    # h2 = h.copy()
    # h2.apply_to_every_coeff(lambda x: centered_modulo(x, divisor))

    # # ====== STEP 2 ======
    # # h1 = h.copy()
    # # h1.apply_to_every_coeff(lambda x: round(x / divisor))
    # # # h1.apply_to_every_coeff(lambda x: centered_modulo(x, 43)) # TODO: fix it
    # h1 = h - h2
    # h1.apply_to_every_coeff(lambda x: x // divisor)

    # # Nikita's version
    # # ====== STEP 1 ======
    # h = r - r_prime
    # h.apply_to_every_coeff(lambda x: centered_modulo(x))

    # # ====== STEP 2 ======
    # h1 = h.copy()
    # h1.apply_to_every_coeff(lambda x: (x // (alpha - 1)))
    # # h1.apply_to_every_coeff(lambda x: centered_modulo(x, 43)) # TODO: fix it

    # # ====== STEP 3 ======
    # h2 = h.copy()
    # h2.apply_to_every_coeff(lambda x: centered_modulo(x, (alpha // 2)))

    # ====== STEP 4 ======
    return h1, h2


def use_hint(
    r: Module.Matrix, h1: Module.Matrix, h2: Module.Matrix, alpha: int
) -> Module.Matrix:
    # ====== STEP 1 ======
    h = h1.scale(alpha, False).add(h2, False)
    # ====== STEP 2 and 3 ======
    return r.sub(h, False)
