from pyteal import *


def approval_program():

    on_creation = Seq(
        [
            Assert(Txn.application_args.length() == Int(3)),
            App.globalPut(Bytes("username"), Txn.application_args[0]),
            App.globalPut(Bytes("usertype"), Txn.application_args[1]),
            App.globalPut(Bytes("email"), Txn.application_args[2]),
            Return(Int(1))
        ]
    )

    update_user = Seq(
        App.globalPut(Bytes("username"), Txn.application_args[0]),
        App.globalPut(Bytes("usertype"), Txn.application_args[1]),
        App.globalPut(Bytes("email"), Txn.application_args[2]),
        Approve()
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.UpdateApplication, update_user]
    )

    return program


if __name__ == "__main__":
    with open("user_contact.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=5)
        f.write(compiled)
