package operations

import (
	"bytes"
	"crypto/rand"
	"encoding/binary"
	"log"
	"os"
	"slices"
	"sync"

	"cyber.ee/pq/devkit"
	"cyber.ee/pq/devkit/poly"
	"cyber.ee/pq/devkit/poly/matrix"
	"cyber.ee/pq/devkit/poly/vector"
	"cyber.ee/pq/topcoat/config"
	"cyber.ee/pq/topcoat/utils"
)

type session struct {
	zFinal     vector.PolyQVector
	rSeedFinal [32]byte
}

type indexPair struct {
	theirIndex int
	mineIndex  int
}

type commitFuncReturnType struct {
	yMine, wMine, wHMine, rMine, c1, c2 vector.PolyQVector
	rMineSeed                           [32]byte
}

func calculateCommitment(skMine utils.TopcoatPrivateKeyShare, A, A1, A2 matrix.PolyQMatrix) commitFuncReturnType {
	// STEP 2
	yMine := vector.NewRandomPolyQVectorWithMaxInfNorm(int(config.Params.L), config.Params.GAMMA-1)

	wMine := A.VecMul(yMine)

	// STEP 3
	wHMine := wMine.HighBits(int64(2 * config.Params.GAMMA_PRIME))

	// STEP 4
	// if config.Params.DIFFERENT_Qs {
	// 	devkit.MainRing = devkit.MainRing.AtLevel(1)
	// }
	rMineSeed := make([]byte, 32)

	_, err := rand.Read(rMineSeed)
	if err != nil {
		panic(err)
	}

	rMine := vector.NewRandomPolyQVectorWithMaxInfNormWithSeed(rMineSeed, int(config.Params.COMMITMENT_K), config.Params.COMMITMENT_BETA)

	// if config.Params.DIFFERENT_Qs {
	// 	devkit.MainRing = devkit.MainRing.AtLevel(0)
	// }

	// STEP 5
	c1, c2 := utils.Commit(A1, A2, wHMine, rMine)
	// log.Println("r:", rMine.CoeffString())
	// log.Println("c1:", c1.CoeffString())

	return commitFuncReturnType{yMine, wMine, wHMine, rMine, c1, c2, [32]byte(rMineSeed)}
}

func Sign(wg *sync.WaitGroup, comms utils.Comms, pk utils.TopcoatPublicKey, skMine utils.TopcoatPrivateKeyShare, message []byte, name string, ret chan utils.TopcoatSignature) {
	defer wg.Done()

	var theirIndexFinal, mineIndexFinal int
	var zTheirFinal, rTheirFinal, c1TheirFinal, c2TheirFinal vector.PolyQVector
	var rTheirSeedFinal [32]byte
	var wHMineListFromParallel, rMineListFromParallel []vector.PolyQVector
	var rMineSeedListFromParallel [][32]byte
	var cHash0Final poly.PolyQ
	var c1CombinedTable, c2CombinedTable, zMineQMatrix [][]vector.PolyQVector

	logger := log.New(os.Stdout, name+": ", log.LstdFlags|log.Lmsgprefix)

	logger.Print("==== START SIGN ====")
	// STEP 1
	ck := utils.Hash4(append(message, pk.Serialize()...))
	logger.Print("calculated ck")

	// STEP X
	ASampler, err := devkit.GetSampler(skMine.ASeed[:])
	if err != nil {
		panic(err)
	}

	A := matrix.NewRandomPolyQMatrix(ASampler, int(config.Params.K), int(config.Params.L))

	// STEP X - in paper, this is "CKeyGen(par)" from top of page 6
	A1, A2 := utils.CommitmentKeys(ck[:])
	logger.Print("calculated A1 and A2")

	// REPEAT STEPS 2-11 until conditions in STEP 11 hold
	iteration := 0
rejection:
	for {
		iteration++
		logger.Printf("IT%d - started calculating commitments", iteration)

		// STEPS 2-5 in THETA parallel sessions
		var wgs sync.WaitGroup
		resultsChan := make(chan commitFuncReturnType, config.Params.PARALLEL_SESSIONS)

		for i := 0; i < int(config.Params.PARALLEL_SESSIONS); i++ {
			wgs.Add(1)
			go func(index int) {
				defer wgs.Done()
				resultsChan <- calculateCommitment(skMine, A, A1, A2)
			}(i)
		}
		wgs.Wait()

		logger.Printf("IT%d - finished calculating commitments", iteration)

		yMineListFromParallel := make([]vector.PolyQVector, config.Params.PARALLEL_SESSIONS)
		wMineListFromParallel := make([]vector.PolyQVector, config.Params.PARALLEL_SESSIONS)
		wHMineListFromParallel = make([]vector.PolyQVector, config.Params.PARALLEL_SESSIONS)
		rMineListFromParallel = make([]vector.PolyQVector, config.Params.PARALLEL_SESSIONS)
		c1MineListFromParallel := make([]vector.PolyQVector, config.Params.PARALLEL_SESSIONS)
		c2MineListFromParallel := make([]vector.PolyQVector, config.Params.PARALLEL_SESSIONS)
		rMineSeedListFromParallel = make([][32]byte, config.Params.PARALLEL_SESSIONS)

		for i := 0; i < int(config.Params.PARALLEL_SESSIONS); i++ {
			commitRet, ok := <-resultsChan
			if !ok {
				log.Panic("Error receiving result")
			}
			// commitRet := calculateCommitment(name, int32(iteration), int32(i), skMine, A1, A2)

			yMineListFromParallel[i] = commitRet.yMine
			wMineListFromParallel[i] = commitRet.wMine
			wHMineListFromParallel[i] = commitRet.wHMine
			rMineListFromParallel[i] = commitRet.rMine
			c1MineListFromParallel[i] = commitRet.c1
			c2MineListFromParallel[i] = commitRet.c2
			rMineSeedListFromParallel[i] = commitRet.rMineSeed
		}

		logger.Printf("IT%d - finished collecting commitments", iteration)

		cMineHash3 := utils.Hash3(
			append(
				matrix.PolyQMatrix(c1MineListFromParallel).Serialize(),
				matrix.PolyQMatrix(c2MineListFromParallel).Serialize()...,
			),
		)

		logger.Printf("IT%d - calculated cMineHash3", iteration)

		comms.Send(cMineHash3)
		logger.Printf("IT%d - sent cMineHash3 to other party", iteration)

		cTheirHash3 := comms.Get().([32]byte)
		logger.Printf("IT%d - received cTheirHash3 from other party", iteration)

		// STEP 7
		comms.Send(c1MineListFromParallel)
		logger.Printf("IT%d - sent c1MineList to other party", iteration)

		c1TheirListFromParallel := comms.Get().([]vector.PolyQVector)
		logger.Printf("IT%d - received c1TheirList from other party", iteration)

		comms.Send(c2MineListFromParallel)
		logger.Printf("IT%d - sent c2MineList to other party", iteration)

		c2TheirListFromParallel := comms.Get().([]vector.PolyQVector)
		logger.Printf("IT%d - received c2TheirList from other party", iteration)

		// STEP 8
		if cTheirHash3 != utils.Hash3(append(
			matrix.PolyQMatrix(c1TheirListFromParallel).Serialize(),
			matrix.PolyQMatrix(c2TheirListFromParallel).Serialize()...,
		),
		) {
			comms.Send(ProtocolMessageABORT)
			logger.Panicf("IT%d - the other side sent invalid c1 and c2", iteration)
		} else {
			comms.Send(ProtocolMessageOK)
		}

		var evalMine, evalTheirs uint64
		err := binary.Read(bytes.NewBuffer(cMineHash3[:]), binary.LittleEndian, &evalMine)
		if err != nil {
			comms.Send(ProtocolMessageERROR)
			logger.Panic(err)
		}
		err = binary.Read(bytes.NewBuffer(cTheirHash3[:]), binary.LittleEndian, &evalTheirs)
		if err != nil {
			comms.Send(ProtocolMessageERROR)
			logger.Panic(err)
		}

		iAmTheOne := evalMine > evalTheirs

		if comms.Get().(utils.ProtocolMessage).Message != utils.ProtocolMessageTypeOK {
			panic("The other side did not send OK")
		}
		logger.Printf("IT%d - checked cTheirHash3", iteration)

		// STEPS 9.A - 11 in THETA x THETA parallel sessions
		// we utilize commitments_combined_matrix, which has THETA x THETA shape
		// rows are index i, columns are index j
		c1CombinedTable = make([][]vector.PolyQVector, config.Params.PARALLEL_SESSIONS)
		c2CombinedTable = make([][]vector.PolyQVector, config.Params.PARALLEL_SESSIONS)
		c0Hash0PolyMatrix := make([][]poly.PolyQ, config.Params.PARALLEL_SESSIONS)
		zMineQMatrix = make([][]vector.PolyQVector, config.Params.PARALLEL_SESSIONS)
		successTableMine := make([][]bool, config.Params.PARALLEL_SESSIONS)

		for theirIndex := 0; theirIndex < int(config.Params.PARALLEL_SESSIONS); theirIndex++ {
			c1CombinedTable[theirIndex] = make([]vector.PolyQVector, config.Params.PARALLEL_SESSIONS)
			c2CombinedTable[theirIndex] = make([]vector.PolyQVector, config.Params.PARALLEL_SESSIONS)
			c0Hash0PolyMatrix[theirIndex] = make([]poly.PolyQ, config.Params.PARALLEL_SESSIONS)
			zMineQMatrix[theirIndex] = make([]vector.PolyQVector, config.Params.PARALLEL_SESSIONS)
			successTableMine[theirIndex] = make([]bool, config.Params.PARALLEL_SESSIONS)

			for mineIndex := 0; mineIndex < int(config.Params.PARALLEL_SESSIONS); mineIndex++ {
				// STEP 9.A - combine commitments "each with each"
				c1CombinedTable[theirIndex][mineIndex] = c1MineListFromParallel[mineIndex].Add(c1TheirListFromParallel[theirIndex])
				c2CombinedTable[theirIndex][mineIndex] = c2MineListFromParallel[mineIndex].Add(c2TheirListFromParallel[theirIndex])

				// STEP 9.B
				// use commitment_combined from i-th row and j-th column
				// both parties will have both c_hash0_poly_matrix (tested)!

				h := []byte{}
				h = append(h, message...)
				h = append(h, c1CombinedTable[theirIndex][mineIndex].Serialize()...)
				h = append(h, c2CombinedTable[theirIndex][mineIndex].Serialize()...)
				h = append(h, pk.Serialize()...)

				c0Hash0PolyMatrix[theirIndex][mineIndex] = utils.Hash0(h)

				// logger.Printf("theirIndex %v, mine Index %v, cHash0: %v", theirIndex, mineIndex, c0Hash0PolyMatrix[theirIndex][mineIndex].CoeffString())

				// STEP 10
				zMineQMatrix[theirIndex][mineIndex] = yMineListFromParallel[mineIndex].Add(skMine.S1.ScaledByPolyProxy(c0Hash0PolyMatrix[theirIndex][mineIndex]))

				// STEP 11

				reject := zMineQMatrix[theirIndex][mineIndex].TransformedToPolyVector().WithCenteredModulo().CheckNormBound(
					int64(config.Params.GAMMA)-int64(config.Params.BETA),
				) || wMineListFromParallel[mineIndex].Sub(
					skMine.S2.ScaledByPolyProxy(
						c0Hash0PolyMatrix[theirIndex][mineIndex],
					)).TransformedToPolyVector().LowBits(
					int64(2*config.Params.GAMMA_PRIME),
				).CheckNormBound(int64(config.Params.GAMMA_PRIME)-int64(config.Params.BETA))

				successTableMine[theirIndex][mineIndex] = !reject
			}
		}

		// STEP X - exchanging success_table, i.e. "good" vector from paper
		comms.Send(successTableMine)
		logger.Printf("IT%d - sent success table to the other party: %v", iteration, successTableMine)

		successTableTheir := comms.Get().([][]bool)
		logger.Printf("IT%d - received success table from the other party", iteration)

		successIndexList := make([]indexPair, 0)

		for mineMiniIndex := 0; mineMiniIndex < int(config.Params.PARALLEL_SESSIONS); mineMiniIndex++ {
			for theirMiniIndex := 0; theirMiniIndex < int(config.Params.PARALLEL_SESSIONS); theirMiniIndex++ {
				if successTableMine[theirMiniIndex][mineMiniIndex] && successTableTheir[mineMiniIndex][theirMiniIndex] {
					successIndexList = append(successIndexList, indexPair{theirMiniIndex, mineMiniIndex})
				}
			}
		}

		logger.Printf("IT%d - found these success pairs: %v", iteration, successIndexList)
		logger.Printf("IT%d - I am the one: %v", iteration, iAmTheOne)
		if iAmTheOne {
			slices.SortFunc(successIndexList, func(a, b indexPair) int {
				if a.theirIndex == b.theirIndex {
					return a.mineIndex - b.mineIndex
				}
				return a.theirIndex - b.theirIndex
			})
		} else {
			slices.SortFunc(successIndexList, func(a, b indexPair) int {
				if a.mineIndex == b.mineIndex {
					return a.theirIndex - b.theirIndex
				}
				return a.mineIndex - b.mineIndex
			})
		}

		logger.Printf("IT%d - sorted success pairs: %v", iteration, successIndexList)

		if len(successIndexList) == 0 {
			comms.Send(ProtocolMessageRESTART)
			logger.Printf("IT%d - didn't find session, restarting", iteration)
		} else {
			theirIndexFinal, mineIndexFinal = successIndexList[0].theirIndex, successIndexList[0].mineIndex
			logger.Printf("IT%d - found session: %v", iteration, successIndexList[0])

			comms.Send(session{
				zFinal:     zMineQMatrix[theirIndexFinal][mineIndexFinal],
				rSeedFinal: rMineSeedListFromParallel[mineIndexFinal],
			})
			logger.Printf("IT%d  - sent zMine and rMine of successfull session to the other party", iteration)
		}

		ret := comms.Get()

		switch t := ret.(type) {
		case utils.ProtocolMessage:
			logger.Printf("IT%d - received message: %v", iteration, t)
			continue rejection
		case session:
			logger.Printf("IT%d - received zTheir and rTheir", iteration)
			zTheirFinal, rTheirSeedFinal = t.zFinal, t.rSeedFinal
			cHash0Final = c0Hash0PolyMatrix[theirIndexFinal][mineIndexFinal]
			c1TheirFinal = c1TheirListFromParallel[theirIndexFinal]
			c2TheirFinal = c2TheirListFromParallel[theirIndexFinal]
			break rejection
		}
	}

	// STEP 13
	wHTheirs := A.VecMul(zTheirFinal).Sub(skMine.Ttheirs.ScaledByPolyProxy(cHash0Final)).HighBits(2 * config.Params.GAMMA_PRIME)

	zTheirFinalT := zTheirFinal.TransformedToPolyVector()
	zTheirFinalT.ApplyToEveryCoeff(func(coeff int64) any {
		return poly.CenteredModulo(coeff, config.Params.Q)
	})

	// STEP 14
	rTheirFinal = vector.NewRandomPolyQVectorWithMaxInfNormWithSeed(rTheirSeedFinal[:], int(config.Params.COMMITMENT_K), config.Params.COMMITMENT_BETA)

	if !utils.OpenCommitment(
		A1, A2, c1TheirFinal, c2TheirFinal, wHTheirs, rTheirFinal,
	) || zTheirFinalT.CheckNormBound(int64(config.Params.GAMMA)-int64(config.Params.BETA)) {
		comms.Send(ProtocolMessageABORT)
		panic("Commitment is not correct")
	} else {
		comms.Send(ProtocolMessageOK)
		logger.Print("Their commitment is correct")
	}

	if comms.Get().(utils.ProtocolMessage).Message != utils.ProtocolMessageTypeOK {
		panic("The other side did not send OK")
	}

	// STEP X
	c1CombinedFinal := c1CombinedTable[theirIndexFinal][mineIndexFinal]
	c2CombinedFinal := c2CombinedTable[theirIndexFinal][mineIndexFinal]
	logger.Print("Calculated c1 and c2 CombinedFinal")

	// STEP 15
	zCombinedFinal := zMineQMatrix[theirIndexFinal][mineIndexFinal].Add(zTheirFinal)
	logger.Print("Calculated zCombinedFinal")

	// STEP 16
	wHroof := wHMineListFromParallel[mineIndexFinal].Add(wHTheirs)
	logger.Print("Calculated whroof")

	// STEP 17
	wH := A.VecMul(zCombinedFinal).Sub(pk.T.ScaledByPolyProxy(cHash0Final).ScaledByInt(devkit.Pow(2, int64(config.Params.D)))).HighBits(2 * int64(config.Params.GAMMA_PRIME))
	logger.Print("Calculated wH")

	// STEP 18
	h1, h2 := utils.Hint(wH.TransformedToPolyVector(), wHroof.TransformedToPolyVector(), devkit.FloorDivision(config.Params.Q-1, 2*config.Params.GAMMA_PRIME))
	logger.Print("Calculated h1 and h2")

	// STEP 19
	signature := utils.TopcoatSignature{
		Z:          zCombinedFinal,
		RSeed1:     rMineSeedListFromParallel[mineIndexFinal],
		RSeed2:     rTheirSeedFinal,
		C1:         c1CombinedFinal,
		C2:         c2CombinedFinal,
		H1:         h1,
		H2:         h2,
		Iterations: iteration,
	}

	ret <- signature
}
