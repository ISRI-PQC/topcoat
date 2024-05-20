import logging
import os
import pickle
import socket
import sys

import click
import yaml

from .helpers.communication import SocketCommunicator
from .keygen import keygen
from .sign import sign
from .verify import verify
from .helpers.logger import get_logger

NAME = "CLI"
VERSION = "0.0.1"
LOGGER = get_logger(logging.INFO, NAME)


@click.group(name="topcoat-group")
@click.option(
    "--debug/--no-debug",
    default=False,
    help="Enable debug mode.",
    is_flag=True,
    show_default=True,
    type=bool,
)
@click.option("--version", "-v", is_flag=True, help="Show version and exit.")
@click.option(
    "--config",
    "-c",
    envvar="TOPCOAT_CONFIG",
    help=(
        "TOPCOAT configuration YAML file or"
        "specify with envvar TOPCOAT_CONFIG"
    ),
    required=True,
)
@click.pass_context
def topcoat_main(ctx, debug, version, config):
    if version:
        click.echo(f"{NAME} version: {VERSION}")
        sys.exit(0)

    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug

    with open(config, "r", encoding="utf-8") as config_file:
        ctx.obj["config"] = yaml.safe_load(config_file)

    if ctx.invoked_subcommand != "verify":
        config = ctx.obj["config"]
        port = config["port"]

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        LOGGER.info("Starting keygen in %s mode", config["mode"])

        if config["mode"] == "client":
            host = config["host"]
            LOGGER.info("Connecting to %s:%d", host, port)

            try:
                s.connect((host, port))
            except Exception as e:
                LOGGER.error("Failed: %s", str(e))
                sys.exit(1)

            LOGGER.info("Connected successfully to %s:%d")

            LOGGER.info("Starting keygen")
            comms = SocketCommunicator(s)

        elif config["mode"] == "server":
            host = (
                socket.gethostbyname(socket.gethostname())
                if config["host"] == "auto"
                else config["host"]
            )
            LOGGER.info("Waiting for connection on %s:%d", host, port)
            s.bind((host, port))
            s.listen()
            client_socket, client_address = s.accept()
            LOGGER.info("Accepted connection from %s", client_address)

            LOGGER.info("Starting keygen")
            comms = SocketCommunicator(client_socket)

        ctx.obj["comms"] = comms


@topcoat_main.command(
    name="keygen",
)
@click.option(
    "--output",
    "-o",
    type=click.File("wb"),
    required=True,
    help="Output file (defaults to 'topcoat_keys.pkl')",
)
@click.pass_context
def topcoat_keygen(
    ctx,
    output,
):
    keys = keygen(ctx.obj["comms"], ctx.obj["config"]["my_name"])

    LOGGER.info("Saving keys to %s", output.name)
    with output:
        pickle.dump(keys, output)


@topcoat_main.command(
    name="sign",
)
@click.option(
    "--keys",
    "-k",
    type=click.File("rb"),
    required=True,
    help="Keys file",
)
@click.option(
    "--message",
    "-m",
    help="Either string to sign or filepath of file to sign",
    required=True,
)
@click.option(
    "--output",
    "-o",
    type=click.File("wb"),
    required=True,
    help="Output file",
)
@click.pass_context
def topcoat_sign(
    ctx,
    keys,
    message,
    output,
):
    with keys:
        keys = pickle.load(keys)

    if os.path.isfile(message):
        with open(message, "rb") as f:
            message = f.readall()
    else:
        message = message.encode()

    signature = sign(
        ctx.obj["comms"],
        keys[0],
        keys[1],
        message,
        ctx.obj["config"]["my_name"],
    )

    LOGGER.info("Saving signature to %s", output.name)
    with output:
        pickle.dump(signature, output)


@topcoat_main.command(
    name="verify",
)
@click.option(
    "--message",
    "-m",
    help="Either string to sign or filepath of file to sign",
    required=True,
)
@click.option(
    "--signature",
    "-s",
    type=click.File("rb"),
    required=True,
    help="Signature file",
)
@click.option(
    "--keys",
    "-k",
    type=click.File("rb"),
    required=True,
    help="Keys file",
)
@click.pass_context
def topcoat_verify(
    ctx,
    message,
    signature,
    keys,
):
    with keys:
        keys = pickle.load(keys)

    if os.path.isfile(message):
        with open(message, "rb") as f:
            message = f.readall()
    else:
        message = message.encode()

    with signature:
        signature = pickle.load(signature)

    result = verify(
        message,
        signature,
        keys[0],
        ctx.obj["config"]["my_name"],
    )

    LOGGER.info("Verification result: %s", result)


if __name__ == "__main__":
    topcoat_main()  # pylint: disable=no-value-for-parameter
