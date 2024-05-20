from dataclasses import dataclass
from typing import Tuple

from .modules import Module


@dataclass
class TopcoatPrivateKeyShare:
    A: Module.Matrix
    t_theirs: Module.Matrix
    s1: Module.Matrix
    s2: Module.Matrix

    def dump(self):
        return (
            self.A.dump()
            + self.t_theirs.dump()
            + self.s1.dump()
            + self.s2.dump()
        )


@dataclass
class TopcoatPublicKey:
    A: Module.Matrix
    t: Module.Matrix

    def dump(self):
        return self.A.dump() + self.t.dump()


@dataclass
class TopcoatSignature:
    z: Module.Matrix
    c: Module.Matrix
    r: Module.Matrix
    h: Tuple[Module.Matrix, Module.Matrix]
