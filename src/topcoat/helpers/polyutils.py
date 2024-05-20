from .. import params


def centered_modulo(x: int, q: int = params.Q) -> int:
    """Returns x mod q, but centered around 0

    Args:
        x (int): number to be modded
        q (int): modulus

    Returns:
        int: x mod q, centered around 0
    """
    ret = x % q
    if ret > (q >> 1):
        ret -= q
    return ret


def decompose(r: int, a: int, q: int):
    """
    Takes an element r and represents
    it as:

    r = r1*a + r0

    With r0 in the range

    -(a << 1) < r0 <= (a << 1)
    """
    r = r % q
    r0 = centered_modulo(r, a)
    r1 = r - r0
    if r1 == q - 1:
        return 0, r0 - 1
    r1 = r1 // a
    assert r == r1 * a + r0
    return r1, r0


def high_bits(r: int, a: int, q: int):
    r1, _ = decompose(r, a, q)
    return r1


def low_bits(r: int, a: int, q: int):
    _, r0 = decompose(r, a, q)
    return r0


def check_norm_bound(n: int, b: int, q: int):
    x = n % q  # x ∈ {0,        ...,                    ...,     q-1}
    x = (
        (q - 1) >> 1
    ) - x  # x ∈ {-(q-1)/2, ...,       -1,       0, ..., (q-1)/2}
    x = x ^ (x >> 31)  # x ∈ { (q-3)/2, ...,        0,       0, ..., (q-1)/2}
    x = (
        (q - 1) >> 1
    ) - x  # x ∈ {0, 1,     ...,  (q-1)/2, (q-1)/2, ...,       1}
    return x >= b
