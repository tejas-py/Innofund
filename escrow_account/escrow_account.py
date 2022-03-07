from pyteal import *


def contract():
    """#pragma version 5
    int 1
"""
    return Approve()


if __name__ == "__main__":
    with open("escrow_account\sample.teal", "w") as f:
        compiled = compileTeal(contract(), mode=Mode.Signature, version=5)
        f.write(compiled)
