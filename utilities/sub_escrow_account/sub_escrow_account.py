from pyteal import *


def escrow_account():

    return Approve()


if __name__ == "__main__":
    with open("sub_escrow_account/sub_escrow_account.teal", "w") as f:
        compiled = compileTeal(escrow_account(), mode=Mode.Signature, version=6)
        f.write(compiled)
