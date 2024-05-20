import os
import sys
from multiprocessing import Queue
from time import time

from . import params
from .helpers.communication import Communicator, ProtocolMessageType
from .helpers.dataclasses import TopcoatPrivateKeyShare, TopcoatPublicKey
from .helpers.exception import ProtocolException
from .helpers.hashes import hash1, hash2
from .helpers.logger import get_logger
from .helpers.ntt_helper import NTTHelperTopcoat
from .helpers.polynomials import PolynomialRing
from .helpers.utils import sample_matrix, sample_vector_with_max_inf_norm

R = PolynomialRing(params.Q, params.N, ntt_helper=NTTHelperTopcoat)


def keygen(comms: Communicator, name: str, return_queue: Queue = None):
    logger = get_logger(params.LOGGING_LEVEL, name)
    logger.debug("=" * 10 + f" START KEYGEN {name}" + "=" * 10)
    pid = os.getpid()
    logger.debug("starting keygen, PID: %d", pid)

    total_time = 0
    # ====== STEP 1 ======
    start = time()
    A_mine = sample_matrix(R, rows=params.K, columns=params.L)
    logger.debug("sampled A_mine matrix")

    # ====== STEP 2 ======
    A_mine_hash1 = hash1(A_mine.dump())
    logger.debug("calculated Hash1 of A_mine")
    total_time += time() - start

    comms.send(A_mine_hash1)
    logger.debug("sent Hash1 of A_mine to the other party")

    A_theirs_hash1 = comms.get()
    logger.debug("received Hash1 of A_theirs from the other party")

    # ====== STEP 3 ======
    comms.send(A_mine)
    logger.debug("sent A_mine to the other party")

    A_theirs = comms.get()
    logger.debug("received A_theirs from the other party")

    # ====== STEP 4 ======
    start = time()
    if hash1(A_theirs.dump()) != A_theirs_hash1:
        comms.send(ProtocolMessageType.ABORT)
        raise ProtocolException("The other side sent invalid matrix A")
    else:
        logger.debug("checked Hash2 of t_theirs")
        total_time += time() - start
        comms.send(ProtocolMessageType.OK)

    assert comms.get() == ProtocolMessageType.OK

    logger.debug("checked Hash1 of A_theirs")

    # ====== STEP 5 ======
    start = time()
    A_combined = A_mine + A_theirs
    logger.debug("combined A_mine and A_theirs")

    # ====== STEP 6 ======
    s1_mine = sample_vector_with_max_inf_norm(
        R, size=params.L, max_inf_norm=params.ETA
    )
    logger.debug("sampled s_1")

    s2_mine = sample_vector_with_max_inf_norm(
        R, size=params.K, max_inf_norm=params.ETA
    )
    logger.debug("sampled s_2")

    # ====== STEP 7 ======
    t_mine = (A_combined @ s1_mine) + s2_mine
    logger.debug("calculated t")

    # ====== STEP 8 ======
    t_mine_hash = hash2(t_mine.dump())
    logger.debug("calculated Hash2 of t_mine")
    total_time += time() - start
    comms.send(t_mine_hash)
    logger.debug("sent Hash2 of t_mine to the other party")

    t_theirs_hash = comms.get()
    logger.debug("received Hash2 of t_theirs from the other party")

    # ====== STEP 9 ======
    comms.send(t_mine)
    logger.debug("sent t_mine to the other party")

    t_theirs = comms.get()
    logger.debug("received t_theirs from the other party")

    # ====== STEP 10 ======
    start = time()
    if hash2(t_theirs.dump()) != t_theirs_hash:
        comms.send(ProtocolMessageType.ABORT)
        raise ProtocolException("The other side sent invalid vector t")
    else:
        logger.debug("checked Hash2 of t_theirs")
        total_time += time() - start
        comms.send(ProtocolMessageType.OK)

    assert comms.get() == ProtocolMessageType.OK

    # ====== STEP 11 ======
    start = time()
    t_combined = t_mine + t_theirs
    logger.debug("combined t_mine and t_theirs")

    # ====== STEP 12 ======
    t_1, _ = t_combined.power_2_round(params.D)
    logger.debug("calculated t_1")
    total_time += time() - start

    # ====== STEP 13 ======
    keys = (
        TopcoatPublicKey(
            A=A_combined,
            t=t_1,
        ),
        TopcoatPrivateKeyShare(
            A=A_combined,
            t_theirs=t_theirs,
            s1=s1_mine,
            s2=s2_mine,
        ),
    )

    logger.info("finished keygen in %f seconds", total_time)

    if return_queue is None:
        return keys
    else:
        return_queue.put(keys)
