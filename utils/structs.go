package utils

import (
	"cyber.ee/pq/latticehelper/poly/vector"
)

type TopcoatPrivateKeyShare struct {
	ASeed           [32]byte
	Ttheirs, S1, S2 vector.PolyQVector
}

type TopcoatPublicKey struct {
	ASeed [32]byte
	T     vector.PolyQVector
}

func (pk TopcoatPublicKey) Serialize() []byte {
	ret := []byte{}
	ret = append(ret, pk.ASeed[:]...)
	ret = append(ret, pk.T.Serialize()...)
	return ret
}

type TopcoatSignature struct {
	Z, C1, C2      vector.PolyQVector
	H1, H2         vector.PolyVector
	RSeed1, RSeed2 [32]byte
	Iterations     int //temp
}

func (sig TopcoatSignature) Serialize() []byte {
	ret := []byte{}
	ret = append(ret, sig.Z.Serialize()...)
	ret = append(ret, sig.RSeed1[:]...)
	ret = append(ret, sig.RSeed2[:]...)
	ret = append(ret, sig.C1.Serialize()...)
	ret = append(ret, sig.C2.Serialize()...)
	ret = append(ret, sig.H1.Serialize()...)
	ret = append(ret, sig.H2.Serialize()...)
	return ret
}
