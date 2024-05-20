import pickle
from enum import Enum
from socket import socket

from .exception import ProtocolException


class ProtocolMessageType(Enum):
    OK = "ok"
    ABORT = "abort"
    RESTART = "restart"
    ERROR = "error"


class Communicator:
    def __init__(self, other_party, from_other_party=None):
        self.other_party = other_party
        self.from_other_party = from_other_party

    def get(self) -> object:
        data = self.get_impl()
        if isinstance(data, ProtocolMessageType) and (
            data == ProtocolMessageType.ABORT
            or data == ProtocolMessageType.ERROR
        ):
            raise ProtocolException("The other side sent: " + data.value)

        return data

    def send(self, data: object):
        self.send_impl(data)

    def send_impl(self, data: object):
        raise NotImplementedError

    def get_impl(self) -> object:
        raise NotImplementedError


class SocketCommunicator(Communicator):
    def __init__(self, other_party: socket):
        super().__init__(other_party)

    def send_impl(self, data: object):
        to_send = pickle.dumps(data)
        length = len(to_send).to_bytes(4, byteorder="big")
        self.other_party.sendall(length + to_send)

    def get_impl(self) -> object:
        self.other_party: socket
        result = b""
        length = int.from_bytes(self.other_party.recv(4), byteorder="big")

        received_data = b""
        while len(received_data) < length:
            chunk = self.other_party.recv(
                min(length - len(received_data), 4096)
            )
            if not chunk:
                break
            received_data += chunk

        return pickle.loads(received_data)


class QueueCommunicator(Communicator):
    def send_impl(self, data: object):
        self.other_party.put(data)

    def get_impl(self) -> object:
        return self.from_other_party.get()
