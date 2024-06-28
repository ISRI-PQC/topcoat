package utils

import (
	"cyber.ee/pq/devkit"
	"cyber.ee/pq/devkit/poly/matrix"
	"cyber.ee/pq/devkit/poly/vector"
	"cyber.ee/pq/topcoat/config"
	"github.com/tuneinsight/lattigo/v5/ring"
	"github.com/tuneinsight/lattigo/v5/utils/sampling"
)

func CommitmentKeys(ck []byte) (matrix.PolyQMatrix, matrix.PolyQMatrix) {
	seededPRNG, err := sampling.NewKeyedPRNG(ck)
	if err != nil {
		panic(err)
	}

	sampler := ring.NewUniformSampler(seededPRNG, devkit.MainRing)

	A1prime := matrix.NewRandomPolyQMatrix(sampler, int(config.Params.COMMITMENT_Nlower), int(config.Params.COMMITMENT_K-config.Params.COMMITMENT_Nlower))

	A1 := matrix.NewIdentityPolyQMatrix(int(config.Params.COMMITMENT_Nlower)).Concat(A1prime).(matrix.PolyQMatrix)

	A2prime := matrix.NewRandomPolyQMatrix(sampler, int(config.Params.COMMITMENT_L), int(config.Params.COMMITMENT_K-config.Params.COMMITMENT_L-config.Params.COMMITMENT_Nlower))

	A2 := matrix.NewZeroPolyQMatrix(int(config.Params.COMMITMENT_L), int(config.Params.COMMITMENT_Nlower)).Concat(matrix.NewIdentityPolyQMatrix(int(config.Params.COMMITMENT_L))).Concat(A2prime).(matrix.PolyQMatrix)

	return A1, A2
}

func Commit(A1, A2 matrix.PolyQMatrix, m, r vector.PolyQVector) (vector.PolyQVector, vector.PolyQVector) {
	c1 := A1.VecMul(r).(vector.PolyQVector)
	c2 := A2.VecMul(r).Add(m).(vector.PolyQVector)
	return c1, c2
}

func OpenCommitment(A1, A2 matrix.PolyQMatrix, c1, c2, m, r vector.PolyQVector) bool {
	c1r := A1.VecMul(r).(vector.PolyQVector)
	c2r := A2.VecMul(r).Add(m).(vector.PolyQVector)

	eq1 := c1r.Equals(c1)
	eq2 := c2r.Equals(c2)

	rsn := r.SecondNorm()
	eq3 := rsn <= float64(config.Params.COMMITMENT_B2)

	return eq1 && eq2 && eq3
}
