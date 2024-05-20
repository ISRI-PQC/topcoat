import sys
from multiprocessing import Pool, Queue
from time import time

from . import params
from .helpers.commitment import commit, commitment_keys, open_commitment
from .helpers.communication import Communicator, ProtocolMessageType
from .helpers.dataclasses import (
    TopcoatPrivateKeyShare,
    TopcoatPublicKey,
    TopcoatSignature,
)
from .helpers.exception import ProtocolException
from .helpers.hashes import eval_commitment, hash0, hash3, hash4
from .helpers.hints import hint
from .helpers.logger import get_logger
from .helpers.modules import Module
from .helpers.ntt_helper import NTTHelperTopcoat
from .helpers.polynomials import PolynomialRing
from .helpers.polyutils import centered_modulo
from .helpers.utils import sample_vector_with_max_inf_norm

R = PolynomialRing(params.Q, params.N, ntt_helper=NTTHelperTopcoat)


def calculate_commitment_func(
    sk_mine: TopcoatPrivateKeyShare,
    A1: Module.Matrix,
    A2: Module.Matrix,
):
    """
    Function to be used in parallel to calculate commitments
    """
    # ====== STEP 2 ======
    y_mine = sample_vector_with_max_inf_norm(R, params.L, params.GAMMA - 1)
    w_mine = sk_mine.A @ y_mine

    # ====== STEP 3 ======
    wH_mine = w_mine.high_bits(2 * params.GAMMA_PRIME)

    # ====== STEP 4 ======
    r_mine = sample_vector_with_max_inf_norm(
        PolynomialRing(
            params.COMMITMENT_Q,
            params.COMMITMENT_N,
            ntt_helper=NTTHelperTopcoat,
        ),
        params.COMMITMENT_K,
        params.COMMITMENT_BETA,
    )

    # ====== STEP 5 ======
    c1, c2 = commit(A1, A2, wH_mine, r_mine)

    return y_mine, w_mine, wH_mine, r_mine, (c1, c2)


def sign(
    comms: Communicator,
    pk: TopcoatPublicKey,
    sk_mine: TopcoatPrivateKeyShare,
    message: bytes,
    name: str,
    return_queue: Queue = None,
):
    """
    This function is executed by BOTH parties at the same time!
    """

    total_time = 0

    logger = get_logger(params.LOGGING_LEVEL, name)
    logger.debug("=" * 10 + f" START SIGN {name}" + "=" * 10)
    logger.debug("starting sign")

    # ====== STEP 1 ======
    start = time()
    ck = hash4(message + pk.dump())
    logger.debug("calculated ck")

    # STEP X - in paper, this is "CKeyGen(par)" from top of page 6
    A1, A2 = commitment_keys(ck)
    logger.debug("calculated A1 and A2")
    total_time += time() - start
    iteration = 0

    # REPEAT STEPS 2-11 until conditions in STEP 11 hold
    while True:
        iteration += 1
        logger.debug("IT%d - starting calculating commitments", iteration)

        # STEPS 2-5 in THETA parallel sessions, see calculate_commitment_func
        # at the top of this file
        with Pool(processes=params.PARALLEL_SESSIONS) as pool:
            result = pool.starmap(
                calculate_commitment_func,
                [(sk_mine, A1, A2)] * params.PARALLEL_SESSIONS,
            )
            (
                y_mine_list_from_parallel,
                w_mine_list_from_parallel,
                wH_mine_list_from_parallel,
                r_mine_list_from_parallel,
                commitments_mine_list_from_parallel,
            ) = zip(*result)

        # (
        #     y_mine_list_from_parallel,
        #     w_mine_list_from_parallel,
        #     wH_mine_list_from_parallel,
        #     r_mine_list_from_parallel,
        #     commitments_mine_list_from_parallel,
        # ) = calculate_commitment_func(sk_mine, A1, A2)

        # y_mine_list_from_parallel = [y_mine_list_from_parallel]
        # w_mine_list_from_parallel = [w_mine_list_from_parallel]
        # wH_mine_list_from_parallel = [wH_mine_list_from_parallel]
        # r_mine_list_from_parallel = [r_mine_list_from_parallel]
        # commitments_mine_list_from_parallel = [
        #     commitments_mine_list_from_parallel
        # ]

        logger.debug("IT%d - finished calculating commitments", iteration)

        # ====== STEP 6 ======
        c_mine_hash3 = hash3(
            b"".join(
                commitment[0].dump() + commitment[1].dump()
                for commitment in commitments_mine_list_from_parallel
            )
        )
        logger.debug("IT%d - calculated c_mine_hash3", iteration)
        total_time += time() - start

        comms.send(c_mine_hash3)
        logger.debug("IT%d - sent c_mine_hash3 to the other party", iteration)

        c_theirs_hash3 = comms.get()
        logger.debug(
            "IT%d - received c_theirs_hash3 from the other party", iteration
        )

        # ====== STEP 7 ======
        comms.send(commitments_mine_list_from_parallel)
        logger.debug("IT%d - sent c_mine to the other party", iteration)

        commitments_their_list_from_parallel = comms.get()
        logger.debug(
            "IT%d - received c_theirs from the other party", iteration
        )

        i_am_the_one = eval_commitment(
            commitments_mine_list_from_parallel
        ) > eval_commitment(commitments_their_list_from_parallel)

        # ====== STEP 8 ======
        start = time()
        if (
            hash3(
                b"".join(
                    commitment[0].dump() + commitment[1].dump()
                    for commitment in commitments_their_list_from_parallel
                )
            )
            != c_theirs_hash3
        ):
            comms.send(ProtocolMessageType.ABORT)
            raise ProtocolException("The other side sent invalid matrix c")
        else:
            total_time += time() - start
            comms.send(ProtocolMessageType.OK)

        assert comms.get() == ProtocolMessageType.OK
        logger.debug("IT%d - checked c_theirs_hash3", iteration)

        # ====== STEPS 9.A - 11 ====== in THETA x THETA parallel sessions
        # we utilize commitments_combined_matrix, which has THETA x THETA shape
        # rows are index i, columns are index j

        # prepare lists for storing rows
        start = time()
        commitments_combined_matrix = []
        c_hash0_poly_matrix = []
        z_mine_matrix = []
        success_table_mine_matrix = []

        # Caution: we cannot use both indexes straight away
        # because at the time of matrix population, the list is empty.
        # That's why there are lot of ".append" calls.

        logger.debug("IT%d - starting THETA x THETA calculations", iteration)
        # "for each row"
        for their_index in range(params.PARALLEL_SESSIONS):
            commitments_combined_matrix.append([])
            c_hash0_poly_matrix.append([])
            z_mine_matrix.append([])
            success_table_mine_matrix.append([])
            # "for each column"
            for mine_index in range(params.PARALLEL_SESSIONS):
                # ====== STEP 9.A ====== - combine commitments "each with each"
                commitments_combined_matrix[their_index].append(
                    (
                        commitments_mine_list_from_parallel[mine_index][0]
                        + commitments_their_list_from_parallel[their_index][0],
                        commitments_mine_list_from_parallel[mine_index][1]
                        + commitments_their_list_from_parallel[their_index][1],
                    )
                )

                # ====== STEP 9.B ======
                # use commitment_combined from i-th row and j-th column
                # [0] is c1, [1] is c2
                # both parties will have both c_hash0_poly_matrix (tested)!
                c_hash0_poly_matrix[their_index].append(
                    hash0(
                        R,
                        message
                        + commitments_combined_matrix[their_index][mine_index][
                            0
                        ].dump()  # c1
                        + commitments_combined_matrix[their_index][mine_index][
                            1
                        ].dump()  # c2
                        + pk.dump(),
                    )
                )

                # ====== STEP 10 ======
                # use c_hash0 from previous step
                z_mine_matrix[their_index].append(
                    (
                        y_mine_list_from_parallel[mine_index]
                        + sk_mine.s1.scale(
                            c_hash0_poly_matrix[their_index][mine_index]
                        )
                    )
                )
                z_mine_matrix[their_index][mine_index].apply_to_every_coeff(
                    centered_modulo
                )

                # ====== STEP 11 ======
                reject = z_mine_matrix[their_index][
                    mine_index
                ].check_norm_bound(params.GAMMA - params.BETA) or (
                    (
                        w_mine_list_from_parallel[mine_index]
                        - sk_mine.s2.scale(
                            c_hash0_poly_matrix[their_index][mine_index]
                        )
                    )
                    .low_bits(2 * params.GAMMA_PRIME)
                    .check_norm_bound(params.GAMMA_PRIME - params.BETA)
                )

                # Save rejection result into success_table matrix
                success_table_mine_matrix[their_index].append(not reject)

        total_time += time() - start
        # STEP X - exchanging success_table, i.e. "good" vector from paper
        comms.send(success_table_mine_matrix)
        logger.debug(
            "IT%d - sent success_table to the other party: %s",
            iteration,
            success_table_mine_matrix,
        )

        success_table_their_matrix = comms.get()
        logger.debug(
            "IT%d - received success_table from the other party: %s",
            iteration,
            success_table_their_matrix,
        )

        # Find first successfull session
        # Remember:this code is executed both by Alice and Bob at the same time
        # So both should find the same session
        start = time()
        found_list = (
            (their_mini_index, mine_mini_index)
            for their_mini_index in range(params.PARALLEL_SESSIONS)
            for mine_mini_index in range(params.PARALLEL_SESSIONS)
            if success_table_mine_matrix[their_mini_index][mine_mini_index]
            and success_table_their_matrix[mine_mini_index][their_mini_index]
        )

        success = False

        if found_list:
            found_common = sorted(
                found_list,
                key=lambda x: (x[0], x[1]) if i_am_the_one else (x[1], x[0]),
            )

            if found_common:
                found_common = found_common[0]
                success = True
                logger.debug(
                    "IT%d - found successfull session (%d, %d)",
                    iteration,
                    found_common[0],
                    found_common[1],
                )

        total_time += time() - start

        # ====== STEP 13 ====== (possibly)
        if not success:
            # If not found, send restart
            comms.send(ProtocolMessageType.RESTART)
            logger.debug(
                "IT%d - didn't found session, sent RESTART to the other party",
                iteration,
            )
        else:
            # If found, save winning session indexes
            their_index_final, mine_index_final = found_common
            # Also send z_mine and r_mine of successfull session
            comms.send(
                (
                    z_mine_matrix[their_index_final][mine_index_final],
                    r_mine_list_from_parallel[mine_index_final],
                ),
            )
            logger.debug(
                "IT%d - sent z_mine and r_mine of successfull"
                "session to the other party",
                iteration,
            )

        # Receive result from the other party
        # It should be either RESTART or tuple of z_theirs and r_theirs
        returned = comms.get()
        if returned == ProtocolMessageType.RESTART:
            logger.debug(
                "IT%d - received RESTART from the other party", iteration
            )
            # If RESTART, continue to next iteration
            continue
        if isinstance(returned, tuple) and len(returned) == 2:
            logger.debug(
                "IT%d - received z_theirs and r_theirs from the other party",
                iteration,
            )
            z_theirs_final, r_theirs_final = returned
            # If tuple, break the loop and continue to STEP 13
            break

    logger.debug("c_hash0_poly")

    start = time()
    # ====== STEP 13 ======
    wH_theirs = (
        sk_mine.A @ z_theirs_final
        - sk_mine.t_theirs.scale(
            c_hash0_poly_matrix[their_index_final][mine_index_final]
        )
    ).high_bits(2 * params.GAMMA_PRIME)
    logger.debug("calculated wH_theirs")

    # temp
    total_low_bits = (
        (
            (
                sk_mine.A
                @ (
                    z_theirs_final
                    + z_mine_matrix[their_index_final][mine_index_final]
                )
            )
            - pk.t.scale(
                c_hash0_poly_matrix[their_index_final][mine_index_final]
            )
        )
        .low_bits(2 * params.GAMMA_PRIME)
        .check_norm_bound(params.GAMMA_PRIME - 2 * params.BETA)
    )
    logger.debug("total_low_bits (true is bad): " + str(total_low_bits))
    # end of temp

    # ====== STEP 14 ======
    if not open_commitment(
        A1,
        A2,
        commitments_their_list_from_parallel[their_index_final][0],
        commitments_their_list_from_parallel[their_index_final][1],
        wH_theirs,
        r_theirs_final,
    ) or z_theirs_final.check_norm_bound(params.GAMMA - params.BETA):
        comms.send(ProtocolMessageType.ABORT)
        raise ProtocolException("Commitment is not correct")
    else:
        total_time += time() - start
        comms.send(ProtocolMessageType.OK)
        logger.debug("sent OK to the other party")

    # Receive OK from the other party
    assert comms.get() == ProtocolMessageType.OK
    logger.debug("checked commitment")

    # STEP X - just saving to variables for easier access
    start = time()
    c_combined_final = commitments_combined_matrix[their_index_final][
        mine_index_final
    ]
    logger.debug("calculated c_combined")

    # ====== STEP 15 ======
    z_combined_final = (
        z_mine_matrix[their_index_final][mine_index_final] + z_theirs_final
    )
    logger.debug("calculated z_combined")
    r_combined_final = (
        r_mine_list_from_parallel[mine_index_final] + r_theirs_final
    )
    logger.debug("calculated r_combined")

    # ====== STEP 16 ======
    wH_roof = wH_mine_list_from_parallel[mine_index_final] + wH_theirs
    logger.debug("calculated wH_roof")

    # ====== STEP 17 ======

    # version with t_1 from keygen:STEP 12 - compressed key
    wH = (
        sk_mine.A @ z_combined_final
        - pk.t.scale(
            c_hash0_poly_matrix[their_index_final][mine_index_final]
        ).scale(2**params.D)
    ).high_bits(2 * params.GAMMA_PRIME)
    logger.debug("calculated wH")

    # ====== STEP 18 ======
    h = hint(wH, wH_roof, (params.Q - 1) // (2 * params.GAMMA_PRIME))
    logger.debug("calculated h")
    total_time += time() - start
    # ====== STEP 19 ======
    signature = TopcoatSignature(
        z=z_combined_final, c=c_combined_final, r=r_combined_final, h=h
    )

    logger.info("finished sign in %f seconds", total_time)

    if return_queue:
        return_queue.put(signature)
    else:
        return signature
