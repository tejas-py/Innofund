from pyteal import *


def approval_program():

    on_creation = Seq(
        [
            Assert(Txn.application_args.length() == Int(1)),
            App.globalPut(Bytes("usertype"), Txn.application_args[0]),
            Return(Int(1))
        ]
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.NoOp, Approve()],
        [Txn.on_completion() == OnComplete.DeleteApplication, Approve()]
    )

    return program


if __name__ == "__main__":
    with open("user_contact.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=6)
        f.write(compiled)
