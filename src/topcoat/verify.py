from time import time

from . import params
from .helpers.commitment import commitment_keys, open_commitment
from .helpers.dataclasses import TopcoatPublicKey, TopcoatSignature
from .helpers.hashes import hash0, hash4
from .helpers.logger import get_logger
from .helpers.ntt_helper import NTTHelperTopcoat
from .helpers.polynomials import PolynomialRing
from .helpers.hints import use_hint

R = PolynomialRing(params.Q, params.N, ntt_helper=NTTHelperTopcoat)


def verify(
    message: bytes,
    signature: TopcoatSignature,
    pk: TopcoatPublicKey,
    name: str,
):
    logger = get_logger(params.LOGGING_LEVEL, name)
    logger.debug("=" * 10 + f" START {name}" + "=" * 10)

    # ====== STEP 1 ======
    start = time()
    ck = hash4(message + pk.dump())
    A1, A2 = commitment_keys(ck)

    # ====== STEP 2 ======
    c_hash0_poly = hash0(
        R, message + signature.c[0].dump() + signature.c[1].dump() + pk.dump()
    )

    # ====== STEP 3 ======

    # version with t_1 from keygen:STEP 12 - compressed key
    wH = (
        pk.A @ signature.z - pk.t.scale(c_hash0_poly).scale(2**params.D)
    ).high_bits(2 * params.GAMMA_PRIME)

    # version with t_total from keygen:STEP 11
    # wH = (pk.A @ signature.z - pk.t_total.scale(c_hash0_poly)).high_bits(
    #     2 * params.GAMMA_PRIME
    # )

    # ====== STEP 4 ======
    wH_roof = use_hint(
        wH,
        signature.h[0],
        signature.h[1],
        (params.Q - 1) // (2 * params.GAMMA_PRIME),
    )

    # ====== STEP 5 ======
    result = open_commitment(
        A1, A2, signature.c[0], signature.c[1], wH_roof, signature.r
    ) and not signature.z.check_norm_bound(2 * (params.GAMMA - params.BETA))

    # ====== STEP 6 ======
    logger.info(
        "result of verification calculated in %f seconds: %s",
        time() - start,
        result,
    )
    return result
