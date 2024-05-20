import logging
import pickle
import random
from multiprocessing import Process, Queue

from topcoat.helpers.logger import get_logger
from topcoat.helpers.communication import QueueCommunicator
from topcoat.keygen import keygen
from topcoat.sign import sign
from topcoat.verify import verify
from topcoat import params

LOAD_KEYS = False
LOAD_SIGNATURES = False


def main():
    logger = get_logger(params.LOGGING_LEVEL, "Main")
    logger.debug("=" * 40 + "START MAIN" + "=" * 40)

    # PREPARATION OF OBJECTS FOR MULTIPROCESSING
    alice_result = Queue()
    bob_result = Queue()

    from_alice_to_bob = Queue()
    from_bob_to_alice = Queue()

    alice_communicator = QueueCommunicator(
        other_party=from_alice_to_bob, from_other_party=from_bob_to_alice
    )
    bob_communicator = QueueCommunicator(
        other_party=from_bob_to_alice, from_other_party=from_alice_to_bob
    )

    # KEYGEN
    if LOAD_KEYS:
        with open("keys.pkl", "rb") as f:
            alice_pk, alice_sk, bob_pk, bob_sk = pickle.load(f)
        logger.debug("Loaded keys from file")
    else:
        # prepare two parties to run keygen function
        alice_keygen = Process(
            target=keygen,
            args=(alice_communicator, "Alice", alice_result),
        )
        bob_keygen = Process(
            target=keygen,
            args=(bob_communicator, "Bob", bob_result),
        )

        # start processes
        alice_keygen.start()
        bob_keygen.start()
        # collect results
        alice_pk, alice_sk = alice_result.get()
        bob_pk, bob_sk = bob_result.get()
        # wait for processes to finish
        alice_keygen.join()
        bob_keygen.join()

        # save keys to file
        with open("keys.pkl", "wb") as f:
            pickle.dump((alice_pk, alice_sk, bob_pk, bob_sk), f)

    # SIGN

    # message = b"Greetings from Alice and Bob! Signed, Alice and Bob."
    if LOAD_SIGNATURES:
        with open("signatures.pkl", "rb") as f:
            alice_sig, bob_sig = pickle.load(f)
        with open("message.pkl", "rb") as f:
            message = pickle.load(f)
        logger.debug("Loaded signatures and message from file")
    else:
        message = random.randbytes(32)
        # prepare processes to run sign function
        alice_sign = Process(
            target=sign,
            args=(
                alice_communicator,
                alice_pk,
                alice_sk,
                message,
                "Alice",
                alice_result,
            ),
        )
        bob_sign = Process(
            target=sign,
            args=(
                bob_communicator,
                bob_pk,
                bob_sk,
                message,
                "Bob",
                bob_result,
            ),
        )

        # start processes
        alice_sign.start()
        bob_sign.start()
        # collect results
        alice_sig = alice_result.get()
        bob_sig = bob_result.get()
        # wait for processes to finish
        alice_sign.join()
        bob_sign.join()
        # TODO: check if both got same signature

        # save signatures to file
        with open("signatures.pkl", "wb") as f:
            pickle.dump((alice_sig, bob_sig), f)
        with open("message.pkl", "wb") as f:
            pickle.dump(message, f)

    # VERIFY
    result1 = verify(
        message, alice_sig, alice_pk, "Verification alice_sig alice_pk"
    )
    result2 = verify(message, bob_sig, bob_pk, "Verification bob_sig bob_pk")
    result3 = verify(
        message, alice_sig, bob_pk, "Verification alice_sig bob_pk"
    )
    result4 = verify(
        message, bob_sig, alice_pk, "Verification bob_sig alice_pk"
    )

    logger.debug(
        "All should be True: %s %s %s %s", result1, result2, result3, result4
    )

    logger.debug("Finished TOPCOAT PoC")


if __name__ == "__main__":
    main()
