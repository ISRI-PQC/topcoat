# MIT License

# Copyright (c) 2022 Giacomo Pope

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import random
from copy import deepcopy
from .polyutils import (
    centered_modulo,
    high_bits,
    low_bits,
    check_norm_bound,
)


class PolynomialRing:
    """
    Initialise the polynomial ring:

        R = GF(q) / (X^n + 1)
    """

    def __init__(self, q, n, ntt_helper=None):
        self.q = q
        self.n = n
        self.element = PolynomialRing.Polynomial
        self.ntt_helper = ntt_helper

    def random_element(self, is_ntt=False):
        coefficients = [random.randint(0, self.q - 1) for _ in range(self.n)]
        return self(coefficients, is_ntt=is_ntt)

    def __call__(self, coefficients, is_ntt=False):
        if isinstance(coefficients, int):
            return self.element(self, [coefficients], is_ntt)
        if not isinstance(coefficients, list):
            raise TypeError(
                "Polynomials should be constructed from a"
                f"list of integers, of length at most d = {self.n}"
            )
        return self.element(self, coefficients, is_ntt)

    def __eq__(self, other):
        return self.n == other.n and self.q == other.q

    def __repr__(self):
        return (
            "Univariate Polynomial Ring in x over Finite Field of"
            f"size {self.q} with modulus x^{self.n} + 1"
        )

    class Polynomial:
        def __init__(self, parent, coefficients, is_ntt=False):
            self.parent = parent
            self.coeffs = self.parse_coefficients(coefficients)
            self.is_ntt = is_ntt

        def is_zero(self):
            """
            Return if polynomial is zero: f = 0
            """
            return all(c == 0 for c in self.coeffs)

        def is_constant(self):
            """
            Return if polynomial is constant: f = c
            """
            return all(c == 0 for c in self.coeffs[1:])

        def apply_to_every_coeff(self, func):
            self.coeffs = [func(c) for c in self.coeffs]
            return self

        def parse_coefficients(self, coefficients):
            """
            Helper function which right pads with zeros
            to allow polynomial construction as
            f = R([1,1,1])
            """
            l = len(coefficients)
            if l > self.parent.n:
                raise ValueError(
                    "Coefficients describe polynomial of degree greater"
                    f"than maximum degree {self.parent.n}"
                )
            elif l < self.parent.n:
                coefficients = coefficients + [
                    0 for _ in range(self.parent.n - l)
                ]
            return coefficients

        def reduce_coefficents(self):
            """
            Reduce all coefficents modulo q
            """
            self.coeffs = [c % self.parent.q for c in self.coeffs]
            return self

        def schoolbook_multiplication(self, other, use_modulo=True):
            """
            Naive implementation of polynomial multiplication
            suitible for all R_q = F_1[X]/(X^n + 1)
            """
            n = self.parent.n
            a = self.coeffs
            b = other.coeffs
            new_coeffs = [0 for _ in range(n)]
            for i in range(n):
                for j in range(0, n - i):
                    new_coeffs[i + j] += a[i] * b[j]
            for j in range(1, n):
                for i in range(n - j, n):
                    new_coeffs[i + j - n] -= a[i] * b[j]

            return [c % self.parent.q if use_modulo else c for c in new_coeffs]

        def to_ntt(self):
            if self.parent.ntt_helper is None:
                raise ValueError(
                    "Can only perform NTT transform when parent element"
                    "has an NTT Helper"
                )
            return self.parent.ntt_helper.to_ntt(self)

        def copy(self):
            return self.parent(deepcopy(self.coeffs), is_ntt=self.is_ntt)

        def copy_to_ntt(self):
            new_poly = self.parent(deepcopy(self.coeffs), is_ntt=self.is_ntt)
            return self.parent.ntt_helper.to_ntt(new_poly)

        def from_ntt(self):
            if self.parent.ntt_helper is None:
                raise ValueError(
                    "Can only perform NTT transform when parent element"
                    "has an NTT Helper"
                )
            return self.parent.ntt_helper.from_ntt(self)

        def copy_from_ntt(self):
            new_poly = self.parent(deepcopy(self.coeffs), is_ntt=self.is_ntt)
            return self.parent.ntt_helper.from_ntt(new_poly)

        def to_montgomery(self):
            """
            Multiply every element by 2^32 mod q

            Only implemented (currently) for n = 256
            """
            if self.parent.ntt_helper is None:
                raise ValueError(
                    "Can only perform Mont. reduction when parent element"
                    "has an NTT Helper"
                )
            return self.parent.ntt_helper.to_montgomery(self)

        def from_montgomery(self):
            """
            Divide every element by 2^32 mod q

            Only implemented (currently) for n = 256
            """
            if self.parent.ntt_helper is None:
                raise ValueError(
                    "Can only perform Mont. reduction when parent element"
                    "has an NTT Helper"
                )
            return self.parent.ntt_helper.from_montgomery(self)

        def ntt_multiplication(self, other):
            """
            Number Theoretic Transform multiplication.
            Only implemented (currently) for n = 256
            """
            if self.parent.ntt_helper is None:
                raise ValueError(
                    "Can only perform ntt reduction when parent element"
                    "has an NTT Helper"
                )
            if not (self.is_ntt and other.is_ntt):
                raise ValueError(
                    "Can only multiply using NTT if both polynomials"
                    "are in NTT form"
                )
            # function in ntt_helper.py
            new_coeffs = self.parent.ntt_helper.ntt_coefficient_multiplication(
                self.coeffs, other.coeffs
            )
            return self.parent(new_coeffs, is_ntt=True)

        def power_2_round(self, d):
            # power_2 = 1 << d
            r1_coeffs = []
            r0_coeffs = []
            for c in self.coeffs:
                r = c % self.parent.q
                r0 = centered_modulo(r, 2**d)
                r1_coeffs.append((r - r0) // (2**d))
                r0_coeffs.append(r0)

            r1_poly = self.parent(r1_coeffs, is_ntt=self.is_ntt)
            r0_poly = self.parent(r0_coeffs, is_ntt=self.is_ntt)

            return r1_poly, r0_poly

        def high_bits(self, alpha):
            coeffs = [high_bits(c, alpha, self.parent.q) for c in self.coeffs]
            return self.parent(coeffs, is_ntt=self.is_ntt)

        def low_bits(self, alpha):
            coeffs = [low_bits(c, alpha, self.parent.q) for c in self.coeffs]
            return self.parent(coeffs, is_ntt=self.is_ntt)

        def check_norm_bound(self, bound):
            """
            Returns true if the inf norm of any coeff
            is greater or equal to the bound.
            """
            return any(
                check_norm_bound(c, bound, self.parent.q) for c in self.coeffs
            )

        def inf_norm(self):
            return max(
                abs(centered_modulo(c, self.parent.q)) for c in self.coeffs
            )

        def negate(self, use_modulo=True):
            """
            Returns -f, by negating all coefficients
            """
            neg_coeffs = [
                (-x % self.parent.q) if use_modulo else -x for x in self.coeffs
            ]
            return self.parent(neg_coeffs, is_ntt=self.is_ntt)

        def add(self, other, use_modulo=True):
            if isinstance(other, PolynomialRing.Polynomial):
                if self.is_ntt ^ other.is_ntt:
                    raise ValueError(
                        f"Both or neither polynomials must be in NTT form before addition"
                    )
                new_coeffs = [
                    (x + y) % self.parent.q if use_modulo else (x + y)
                    for x, y in zip(self.coeffs, other.coeffs)
                ]
            elif isinstance(other, int):
                new_coeffs = self.coeffs.copy()
                new_coeffs[0] = (
                    (new_coeffs[0] + other) % self.parent.q
                    if use_modulo
                    else (new_coeffs[0] + other)
                )
            else:
                raise NotImplementedError(
                    f"Polynomials can only be added to each other"
                )
            return self.parent(new_coeffs, is_ntt=self.is_ntt)

        def __add__(self, other):
            return self.add(other)

        def __radd__(self, other):
            return self.add(other)

        def __iadd__(self, other):
            self = self.add(other)
            return self

        def sub(self, other, use_modulo=True):
            if self.is_ntt ^ other.is_ntt:
                raise ValueError(
                    f"Both or neither polynomials must be in NTT form before substitution"
                )
            if isinstance(other, PolynomialRing.Polynomial):
                new_coeffs = [
                    (x - y) % self.parent.q if use_modulo else (x - y)
                    for x, y in zip(self.coeffs, other.coeffs)
                ]
            elif isinstance(other, int):
                new_coeffs = self.coeffs.copy()
                new_coeffs[0] = (
                    (new_coeffs[0] - other) % self.parent.q
                    if use_modulo
                    else (new_coeffs[0] - other)
                )
            else:
                raise NotImplementedError(
                    f"Polynomials can only be subracted from each other"
                )
            return self.parent(new_coeffs, is_ntt=self.is_ntt)

        def __sub__(self, other):
            return self.sub(other)

        def __rsub__(self, other):
            return self.sub(other)

        def __isub__(self, other):
            self = self.sub(other)
            return self

        def mul(self, other, use_modulo=True):
            if isinstance(other, PolynomialRing.Polynomial):
                if self.is_ntt and other.is_ntt:
                    return self.ntt_multiplication(other)
                elif self.is_ntt ^ other.is_ntt:
                    raise ValueError(
                        f"Both or neither polynomials must be in NTT form before multiplication"
                    )
                else:
                    new_coeffs = self.schoolbook_multiplication(
                        other, use_modulo
                    )
            elif isinstance(other, int):
                new_coeffs = [
                    (c * other) % self.parent.q if use_modulo else (c * other)
                    for c in self.coeffs
                ]
            else:
                raise NotImplementedError(
                    f"Polynomials can only be multiplied by each other, or scaled by integers"
                )
            return self.parent(new_coeffs, is_ntt=self.is_ntt)

        def __mul__(self, other):
            return self.mul(other)

        def __rmul__(self, other):
            return self.mul(other)

        def __imul__(self, other):
            self = self.mul(other)
            return self

        # def __pow__(self, n):
        #     if not isinstance(n, int):
        #         raise TypeError(
        #             f"Exponentiation of a polynomial must be done using an integer."
        #         )

        #     # Deal with negative scalar multiplication
        #     if n < 0:
        #         raise ValueError(
        #             f"Negative powers are not supported for elements of a Polynomial Ring"
        #         )
        #     f = self
        #     g = self.parent(1, is_ntt=self.is_ntt)
        #     while n > 0:
        #         if n % 2 == 1:
        #             g = g * f
        #         f = f * f
        #         n = n // 2
        #     return g

        def __eq__(self, other):
            if isinstance(other, PolynomialRing.Polynomial):
                return (
                    self.coeffs == other.coeffs and self.is_ntt == other.is_ntt
                )
            elif isinstance(other, int):
                if (
                    self.is_constant()
                    and (other % self.parent.q) == self.coeffs[0]
                ):
                    return True
            return False

        def __getitem__(self, idx):
            return self.coeffs[idx]

        def __repr__(self):
            """
            TODO make this look nice when there
            are negative coeffs...
            """
            ntt_info = ""
            if self.is_ntt:
                ntt_info = " (NTT form)"
            if self.is_zero():
                return "0" + ntt_info

            info = []
            for i, c in enumerate(self.coeffs):
                if c != 0:
                    if i == 0:
                        info.append(f"{c}")
                    elif i == 1:
                        if c == 1:
                            info.append("x")
                        else:
                            info.append(f"{c}*x")
                    else:
                        if c == 1:
                            info.append(f"x^{i}")
                        else:
                            info.append(f"{c}*x^{i}")
            return " + ".join(info) + ntt_info

        def __str__(self):
            return self.__repr__()
