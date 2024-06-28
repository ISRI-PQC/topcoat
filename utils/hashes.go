package utils

import (
	"math/rand/v2"

	"cyber.ee/pq/devkit"
	"cyber.ee/pq/devkit/poly"
	"cyber.ee/pq/topcoat/config"
	"github.com/hashicorp/go-set"
	"golang.org/x/crypto/sha3"
)

func hash(data []byte, seed string) [32]byte {
	seedb := []byte(seed)
	data = append(seedb, data...)
	res := sha3.Sum256(data)
	return res
}

func Hash0(data []byte) poly.PolyQ {
	hb := hash(data, "Hash0")

	r := rand.New(rand.NewChaCha8(hb))
	coeffs := make([]int64, devkit.MainRing.N())

	dropoutPositions := set.New[int](int(config.Params.N - config.Params.TAU))

	for i := 0; i < int(config.Params.N-config.Params.TAU); {
		pos := r.IntN(int(config.Params.N))
		if dropoutPositions.Insert(pos) {
			i++
		}
	}

	for i := 0; i < len(coeffs); i++ {
		if dropoutPositions.Contains(i) {
			continue
		}

		f := r.Float64()
		if f > 0.5 {
			coeffs[i] = -1
		} else {
			coeffs[i] = 1
		}
	}

	return poly.NewPolyQFromCoeffs(coeffs...)
}

func Hash1(data []byte) [32]byte {
	return hash(data, "hash1")
}
func Hash2(data []byte) [32]byte {
	return hash(data, "hash2")
}

func Hash3(data []byte) [32]byte {
	return hash(data, "hash3")
}

func Hash4(data []byte) [32]byte {
	return hash(data, "hash4")
}
