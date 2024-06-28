package operations

import (
	"cyber.ee/pq/devkit"
	"cyber.ee/pq/devkit/poly/matrix"
	"cyber.ee/pq/devkit/poly/vector"
	"cyber.ee/pq/topcoat/config"
	"cyber.ee/pq/topcoat/utils"
)

func Verify(message []byte, signature utils.TopcoatSignature, pk utils.TopcoatPublicKey) bool {
	// STEP 1
	ck := utils.Hash4(append(message, pk.Serialize()...))
	A1, A2 := utils.CommitmentKeys(ck[:])

	// STEP 2
	h := []byte{}
	h = append(h, message...)
	h = append(h, signature.C1.Serialize()...)
	h = append(h, signature.C2.Serialize()...)
	h = append(h, pk.Serialize()...)
	cHash0 := utils.Hash0(h)

	ASampler, err := devkit.GetSampler(pk.ASeed[:])
	if err != nil {
		panic(err)
	}

	// STEP 1
	A := matrix.NewRandomPolyQMatrix(ASampler, int(config.Params.K), int(config.Params.L))

	// STEP 3
	wH := A.VecMul(signature.Z).Sub(pk.T.ScaleByPolyProxy(cHash0).ScaleByInt(devkit.Pow(2, int64(config.Params.D)))).(vector.PolyQVector).HighBits(2 * int64(config.Params.GAMMA_PRIME))

	// STEP 4
	wHroof := utils.UseHint(wH.TransformedToPolyVector(), signature.H1, signature.H2, devkit.FloorDivision(config.Params.Q-1, 2*config.Params.GAMMA_PRIME))

	r1 := vector.NewRandomPolyQVectorWithMaxInfNormWithSeed(signature.RSeed1[:], int(config.Params.COMMITMENT_K), config.Params.COMMITMENT_BETA)
	r2 := vector.NewRandomPolyQVectorWithMaxInfNormWithSeed(signature.RSeed2[:], int(config.Params.COMMITMENT_K), config.Params.COMMITMENT_BETA)

	rCombined := r1.Add(r2).(vector.PolyQVector)

	// STEP 5
	result := utils.OpenCommitment(A1, A2, signature.C1, signature.C2, wHroof.TransformedToPolyQVector(), rCombined) && !signature.Z.TransformedToPolyVector().CheckNormBound(2*(int64(config.Params.GAMMA)-int64(config.Params.COMMITMENT_BETA)))

	return result
}