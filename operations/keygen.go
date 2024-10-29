package operations

import (
	"crypto/rand"
	"log"
	"os"
	"sync"

	"cyber.ee/pq/latticehelper"
	"cyber.ee/pq/latticehelper/poly/matrix"
	"cyber.ee/pq/latticehelper/poly/vector"
	"cyber.ee/pq/topcoat/config"
	"cyber.ee/pq/topcoat/utils"
)

type KeygenResult struct {
	Pk utils.TopcoatPublicKey
	Sk utils.TopcoatPrivateKeyShare
}

func Keygen(wg *sync.WaitGroup, comms utils.Comms, name string, ret chan KeygenResult) {
	defer wg.Done()
	logger := log.New(os.Stdout, name+": ", log.LstdFlags|log.Lmsgprefix)

	logger.Print("==== START KEYGEN ====")

	// STEP 1
	var AMineSeed [32]byte

	_, err := rand.Read(AMineSeed[:])
	if err != nil {
		panic(err)
	}
	logger.Print("Got AMineSeed ")

	// STEP 2
	AMineSeedHash1 := utils.Hash1(AMineSeed[:])
	logger.Print("Calculated Hash1 of AMine")
	comms.Send(AMineSeedHash1)
	logger.Print("Sent Hash1 of AMine to the other party")

	ATheirsSeedHash1 := comms.Get().([32]byte)
	logger.Print("Received Hash1 of AMine from the other party")

	// STEP 3
	comms.Send(AMineSeed)
	logger.Print("Sent AMineSeed to the other party")
	ATheirSeed := comms.Get().([32]byte)
	logger.Print("Received AMine from the other party")

	// STEP 4
	if utils.Hash1(ATheirSeed[:]) != ATheirsSeedHash1 {
		comms.Send(ProtocolMessageABORT)
		panic("The other side sent invalid matrix A")
	} else {
		comms.Send(ProtocolMessageOK)
	}

	if comms.Get().(utils.ProtocolMessage).Message != utils.ProtocolMessageTypeOK {
		panic("The other side did not send OK")
	}

	// STEP 5
	var ASeedCombined [32]byte

	for i := range ASeedCombined {
		ASeedCombined[i] = AMineSeed[i] ^ ATheirSeed[i]
	}

	ASampler, err := latticehelper.GetSampler(ASeedCombined[:])
	if err != nil {
		panic(err)
	}

	// STEP 1
	ACombined := matrix.NewRandomPolyQMatrix(ASampler, int(config.Params.K), int(config.Params.L))

	// STEP 6
	s1Mine := vector.NewRandomPolyQVectorWithMaxInfNorm(int(config.Params.L), config.Params.ETA)
	s2Mine := vector.NewRandomPolyQVectorWithMaxInfNorm(int(config.Params.K), config.Params.ETA)
	logger.Print("sampled s1 and s2")

	// STEP 7
	tMine := ACombined.VecMul(s1Mine).Add(s2Mine)
	logger.Print("computed t")

	// STEP 8
	tMineHash := utils.Hash2(tMine.Serialize())
	logger.Print("computed t hash")
	comms.Send(tMineHash)
	logger.Print("sent t hash")

	tTheirsHash := comms.Get().([32]byte)
	logger.Print("received t hash")

	// STEP 9
	comms.Send(tMine)
	logger.Print("sent t")
	tTheirs := comms.Get().(vector.PolyQVector)
	logger.Print("received t")

	// STEP 10
	if utils.Hash2(tTheirs.Serialize()) != tTheirsHash {
		comms.Send(utils.ProtocolMessageTypeABORT)
		panic("The other side sent invalid vector t")
	} else {
		comms.Send(utils.ProtocolMessageTypeOK)
	}

	if comms.Get().(string) != utils.ProtocolMessageTypeOK {
		panic("The other side did not send OK")
	}

	// STEP 11
	tCombined := tMine.Add(tTheirs)
	logger.Print("computed combined t")

	// STEP 12
	t1, _ := tCombined.Power2Round(config.Params.D)
	logger.Print("computed t1")

	// STEP 13
	ret <- KeygenResult{
		utils.TopcoatPublicKey{
			ASeed: ASeedCombined,
			T:     t1,
		},
		utils.TopcoatPrivateKeyShare{
			ASeed:   ASeedCombined,
			Ttheirs: tTheirs,
			S1:      s1Mine,
			S2:      s2Mine,
		},
	}
}

// import os
// import sys
// from multiprocessing import Queue
// from time import time

// from . import params
// from .helpers.communication import Communicator, ProtocolMessageType
// from .helpers.dataclasses import TopcoatPrivateKeyShare, TopcoatPublicKey
// from .helpers.exception import ProtocolException
// from .helpers.hashes import hash1, hash2
// from .helpers.logger import get_logger
// from .helpers.ntt_helper import NTTHelperTopcoat
// from .helpers.polynomials import PolynomialRing
// from .helpers.utils import sample_matrix, sample_vector_with_max_inf_norm

// R = PolynomialRing(params.Q, params.N, ntt_helper=NTTHelperTopcoat)

// def keygen(comms: Communicator, name: str, return_queue: Queue = None):
//     logger = get_logger(params.LOGGING_LEVEL, name)
//     logger.debug("=" * 10 + f" START KEYGEN {name}" + "=" * 10)
//     pid = os.getpid()
//     logger.debug("starting keygen, PID: %d", pid)

//     total_time = 0
//     # ====== STEP 1 ======
//     start = time()
//     A_mine = sample_matrix(R, rows=params.K, columns=params.L)
//     logger.debug("sampled A_mine matrix")

//     # ====== STEP 2 ======
//     A_mine_hash1 = hash1(A_mine.dump())
//     logger.debug("calculated Hash1 of A_mine")
//     total_time += time() - start

//     comms.send(A_mine_hash1)
//     logger.debug("sent Hash1 of A_mine to the other party")

//     A_theirs_hash1 = comms.get()
//     logger.debug("received Hash1 of A_theirs from the other party")

//     # ====== STEP 3 ======
//     comms.send(A_mine)
//     logger.debug("sent A_mine to the other party")

//     A_theirs = comms.get()
//     logger.debug("received A_theirs from the other party")

//     # ====== STEP 4 ======
//     start = time()
//     if hash1(A_theirs.dump()) != A_theirs_hash1:
//         comms.send(ProtocolMessageType.ABORT)
//         raise ProtocolException("The other side sent invalid matrix A")
//     else:
//         logger.debug("checked Hash2 of t_theirs")
//         total_time += time() - start
//         comms.send(ProtocolMessageType.OK)

//     assert comms.get() == ProtocolMessageType.OK

//     logger.debug("checked Hash1 of A_theirs")

//     # ====== STEP 5 ======
//     start = time()
//     A_combined = A_mine + A_theirs
//     logger.debug("combined A_mine and A_theirs")

//     # ====== STEP 6 ======
//     s1_mine = sample_vector_with_max_inf_norm(
//         R, size=params.L, max_inf_norm=params.ETA
//     )
//     logger.debug("sampled s_1")

//     s2_mine = sample_vector_with_max_inf_norm(
//         R, size=params.K, max_inf_norm=params.ETA
//     )
//     logger.debug("sampled s_2")

//     # ====== STEP 7 ======
//     t_mine = (A_combined @ s1_mine) + s2_mine
//     logger.debug("calculated t")

//     # ====== STEP 8 ======
//     t_mine_hash = hash2(t_mine.dump())
//     logger.debug("calculated Hash2 of t_mine")
//     total_time += time() - start
//     comms.send(t_mine_hash)
//     logger.debug("sent Hash2 of t_mine to the other party")

//     t_theirs_hash = comms.get()
//     logger.debug("received Hash2 of t_theirs from the other party")

//     # ====== STEP 9 ======
//     comms.send(t_mine)
//     logger.debug("sent t_mine to the other party")

//     t_theirs = comms.get()
//     logger.debug("received t_theirs from the other party")

//     # ====== STEP 10 ======
//     start = time()
//     if hash2(t_theirs.dump()) != t_theirs_hash:
//         comms.send(ProtocolMessageType.ABORT)
//         raise ProtocolException("The other side sent invalid vector t")
//     else:
//         logger.debug("checked Hash2 of t_theirs")
//         total_time += time() - start
//         comms.send(ProtocolMessageType.OK)

//     assert comms.get() == ProtocolMessageType.OK

//     # ====== STEP 11 ======
//     start = time()
//     t_combined = t_mine + t_theirs
//     logger.debug("combined t_mine and t_theirs")

//     # ====== STEP 12 ======
//     t_1, _ = t_combined.power_2_round(params.D)
//     logger.debug("calculated t_1")
//     total_time += time() - start

//     # ====== STEP 13 ======
//     keys = (
//         TopcoatPublicKey(
//             A=A_combined,
//             t=t_1,
//             t_total=t_combined,
//         ),
//         TopcoatPrivateKeyShare(
//             A=A_combined,
//             t_theirs=t_theirs,
//             s1=s1_mine,
//             s2=s2_mine,
//         ),
//     )

//     logger.info("finished keygen in %f seconds", total_time)

//     if return_queue is None:
//         return keys
//     else:
//         return_queue.put(keys)
