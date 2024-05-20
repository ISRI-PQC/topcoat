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

import json
import math

from typing import List
from .polynomials import PolynomialRing


class Module:
    def __init__(self, ring):
        self.ring = ring

    def eye(self, size, is_ntt=False):
        return self(
            [
                [
                    (
                        self.ring([1], is_ntt)
                        if i == j
                        else self.ring([0], is_ntt)
                    )
                    for i in range(size)
                ]
                for j in range(size)
            ]
        )

    def zeros(self, rows, columns, is_ntt=False):
        return self(
            [
                [self.ring([0], is_ntt) for _ in range(columns)]
                for _ in range(rows)
            ]
        )

    def __repr__(self):
        return f"Module over the commutative ring: {self.ring}"

    def __str__(self):
        return f"Module over the commutative ring: {self.ring}"

    def __eq__(self, other):
        return self.ring == other.ring

    def __call__(self, matrix_elements):
        if not isinstance(matrix_elements, list):
            raise TypeError(
                "Elements of a module are matrices,"
                f"with elements {self.ring.element}."
            )

        if isinstance(matrix_elements[0], list):
            for element_list in matrix_elements:
                if not all((aij.parent == self.ring) for aij in element_list):
                    raise TypeError(
                        "All elements of the matrix must"
                        f"be elements of the ring: {self.ring}"
                    )
            return Module.Matrix(self, matrix_elements)

        elif isinstance(matrix_elements[0], self.ring.element):
            if not all((aij.parent == self.ring) for aij in matrix_elements):
                raise TypeError(
                    "All elements of the matrix must"
                    f"be elements of the ring: {self.ring}"
                )
            return Module.Matrix(self, [matrix_elements])

        else:
            raise TypeError(
                "Elements of a module are matrices,"
                "built from elements of the base ring."
            )

    class Matrix:
        def __init__(
            self,
            parent,
            matrix_elements: List[List[PolynomialRing.Polynomial]],
        ):
            self.parent = parent
            self.elements = matrix_elements
            self.rows = len(matrix_elements)
            self.cols = len(matrix_elements[0])
            if not self.check_dimensions():
                raise ValueError("Inconsistent row lengths in matrix")

        def with_changed_ring(self, new_ring):
            new_elements = [
                [new_ring(ele.coeffs) for ele in row] for row in self.elements
            ]
            return Module(new_ring)(new_elements)

        def coeffs(self):
            return [[poly.coeffs for poly in row] for row in self.elements]

        def dump(self) -> bytes:
            return json.dumps(self.coeffs()).encode("utf-8")

        def inf_norm(self):
            return max(ele.inf_norm() for row in self.elements for ele in row)

        def second_norm(self):
            return math.sqrt(
                sum(
                    ele.inf_norm() ** 2 for row in self.elements for ele in row
                )
            )

        def shape(self):
            return self.rows, self.cols

        def check_dimensions(self):
            return all(len(row) == self.cols for row in self.elements)

        def transpose(self):
            new_rows = [list(item) for item in zip(*self.elements)]
            return self.parent(new_rows)

        def transpose_self(self):
            self.rows, self.cols = self.cols, self.rows
            self.elements = [list(item) for item in zip(*self.elements)]
            return self

        def reduce_coefficents(self):
            for row in self.elements:
                for ele in row:
                    ele.reduce_coefficents()
            return self

        def to_montgomery(self):
            for row in self.elements:
                for ele in row:
                    ele.to_montgomery()
            return self

        def from_montgomery(self):
            for row in self.elements:
                for ele in row:
                    ele.from_montgomery()
            return self

        def apply_to_every_coeff(self, func):
            for row in self.elements:
                for ele in row:
                    ele.apply_to_every_coeff(func)
            return self

        def scale(self, other, use_modulo=True, use_ntt=True):
            """
            Multiply each element of the matrix by a polynomial or integer
            """
            if not (
                isinstance(other, self.parent.ring.Polynomial)
                or isinstance(other, int)
            ):
                raise TypeError(
                    "Can only multiply elements with polynomials or integers"
                )

            matrix = [
                [
                    (
                        (
                            ele.copy_to_ntt()
                            .mul(other.copy_to_ntt())
                            .copy_from_ntt()
                        ).reduce_coefficents()
                        if use_ntt
                        and isinstance(other, self.parent.ring.Polynomial)
                        else ele.mul(other, use_modulo)
                    )
                    for ele in row
                ]
                for row in self.elements
            ]
            return self.parent(matrix)

        def check_norm_bound(self, bound):
            for row in self.elements:
                if any(p.check_norm_bound(bound) for p in row):
                    return True
            return False

        def power_2_round(self, d):
            """
            Applies `power_2_round` on every element in the
            Matrix to create two matrices.
            """
            m1_elements = [
                [0 for _ in range(self.cols)] for _ in range(self.rows)
            ]
            m0_elements = [
                [0 for _ in range(self.cols)] for _ in range(self.rows)
            ]

            for i in range(self.rows):
                for j in range(self.cols):
                    m1_ele, m0_ele = self[i][j].power_2_round(d)
                    m1_elements[i][j] = m1_ele
                    m0_elements[i][j] = m0_ele

            return self.parent(m1_elements), self.parent(m0_elements)

        def to_ntt(self):
            for row in self.elements:
                for ele in row:
                    ele.to_ntt()
            return self

        def from_ntt(self):
            for row in self.elements:
                for ele in row:
                    ele.from_ntt()
            return self

        def copy(self):
            matrix = [[ele.copy() for ele in row] for row in self.elements]
            return self.parent(matrix)

        def copy_to_ntt(self):
            matrix = [
                [ele.copy_to_ntt() for ele in row] for row in self.elements
            ]
            return self.parent(matrix)

        def copy_from_ntt(self):
            matrix = [
                [ele.copy_from_ntt() for ele in row] for row in self.elements
            ]
            return self.parent(matrix)

        def high_bits(self, alpha):
            matrix = [
                [ele.high_bits(alpha) for ele in row] for row in self.elements
            ]
            return self.parent(matrix)

        def low_bits(self, alpha):
            matrix = [
                [ele.low_bits(alpha) for ele in row] for row in self.elements
            ]
            return self.parent(matrix)

        def __getitem__(self, i):
            return self.elements[i]

        def __eq__(self, other):
            return other.elements == self.elements

        def __or__(self, other):
            """
            Denoted A | B
            """
            if not isinstance(other, Module.Matrix):
                raise TypeError(
                    "Can only concatenate matrcies with other matrices"
                )
            if self.parent != other.parent:
                raise TypeError("Matricies must have the same base ring")
            if self.rows != other.rows:
                raise ValueError("Matrices are of incompatible dimensions")

            new_elements = []
            for i in range(self.rows):
                new_elements.append(self.elements[i] + other.elements[i])
            return self.parent(new_elements)

        def add(self, other, use_modulo=True):
            if not isinstance(other, Module.Matrix):
                raise TypeError("Can only add matrcies to other matrices")
            if self.parent != other.parent:
                raise TypeError("Matricies must have the same base ring")
            if self.shape() != other.shape():
                raise ValueError("Matrices are not of the same dimensions")

            new_elements = []
            for i in range(self.rows):
                new_elements.append(
                    [
                        a.add(b, use_modulo)
                        for a, b in zip(self.elements[i], other.elements[i])
                    ]
                )
            return self.parent(new_elements)

        def __add__(self, other):
            return self.add(other)

        def __radd__(self, other):
            return self.add(other)

        def __iadd__(self, other):
            self = self.add(other)
            return self

        def sub(self, other, use_modulo=True):
            if not isinstance(other, Module.Matrix):
                raise TypeError(
                    "Can only subtract matrcies from other matrices"
                )
            if self.parent != other.parent:
                raise TypeError("Matricies must have the same base ring")
            if self.shape() != other.shape():
                raise ValueError("Matrices are not of the same dimensions")

            new_elements = []
            for i in range(self.rows):
                new_elements.append(
                    [
                        a.sub(b, use_modulo)
                        for a, b in zip(self.elements[i], other.elements[i])
                    ]
                )
            return self.parent(new_elements)

        def __sub__(self, other):
            return self.sub(other)

        def __rsub__(self, other):
            return self.sub(other)

        def __isub__(self, other):
            self = self.sub(other)
            return self

        def matmul(self, other, use_modulo=True, use_ntt=True):
            """
            Denoted A @ B
            """
            if not isinstance(other, Module.Matrix):
                raise TypeError(
                    "Can only multiply matrcies with other matrices"
                )
            if (self.parent) != other.parent:
                print(self.parent, "\n", other.parent)
                raise TypeError("Matricies must have the same base ring")
            if self.cols != other.rows:
                raise ValueError("Matrices are of incompatible dimensions")

            new_elements = [
                [
                    sum(
                        (
                            (
                                a.copy_to_ntt()
                                .mul(b.copy_to_ntt())
                                .copy_from_ntt()
                            ).reduce_coefficents()
                            if use_ntt
                            else a.mul(b, use_modulo)
                        )
                        for a, b in zip(A_row, B_col)
                    )
                    for B_col in other.transpose().elements
                ]
                for A_row in self.elements
            ]
            return self.parent(new_elements)

        def __matmul__(self, other):
            return self.matmul(other)

        def __repr__(self):
            if len(self.elements) == 1:
                return str(self.elements[0])
            max_col_width = []
            for n_col in range(self.cols):
                max_col_width.append(
                    max(len(str(row[n_col])) for row in self.elements)
                )
            info = "]\n[".join(
                [
                    ", ".join(
                        [
                            f"{str(x):>{max_col_width[i]}}"
                            for i, x in enumerate(r)
                        ]
                    )
                    for r in self.elements
                ]
            )
            return f"[{info}]"
