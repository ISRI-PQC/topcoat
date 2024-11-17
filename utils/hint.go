package utils

import (
	"github.com/isri-pqc/latticehelper"
	"github.com/isri-pqc/latticehelper/poly"
	"github.com/isri-pqc/latticehelper/poly/vector"
)

func Hint(r, rPrime vector.PolyVector, alpha int64) (vector.PolyVector, vector.PolyVector) {
	h := r.Sub(rPrime)

	h2 := make(vector.PolyVector, h.Length())

	for i := range h2 {
		h2[i] = poly.NewPoly()
		copy(h2[i], h[i])
	}

	h2.ApplyToEveryCoeff(func(c int64) any {
		return poly.CenteredModulo(c, alpha)
	})

	h1 := h.Sub(h2)
	h1.ApplyToEveryCoeff(func(c int64) any {
		return latticehelper.FloorDivision(c, int64(alpha))
	})

	return h1, h2
}

func UseHint(r, h1, h2 vector.PolyVector, alpha int64) vector.PolyVector {
	h := h1.ScaledByInt(alpha).Add(h2)
	return r.Sub(h)
}
