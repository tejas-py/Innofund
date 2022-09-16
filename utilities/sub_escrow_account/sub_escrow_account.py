from pyteal import *


def escrow_account():

    program = Cond(
        [Bytes('CASHDILLO ESCROW ACCOUNT') == Bytes(), Approve()],
        [Txn.application_id() == Int(0), Approve()],
        [Txn.on_completion() == OnComplete.NoOp, Approve()],
        [Txn.on_completion() == OnComplete.DeleteApplication, Approve()]
    )

    return program


if __name__ == "__main__":
    with open("sub_escrow_account.teal", "w") as f:
        compiled = compileTeal(escrow_account(), mode=Mode.Signature, version=6)
        f.write(compiled)
