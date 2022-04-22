from pyteal import *


def approval_program():

    on_creation = Seq(
        [
            Assert(Txn.application_args.length() == Int(4)),
            App.globalPut(Bytes("username"), Txn.application_args[0]),
            App.globalPut(Bytes("usertype"), Txn.application_args[1]),
            App.globalPut(Bytes("email"), Txn.application_args[2]),
            App.globalPut(Bytes("password"), Txn.application_args[3]),
            Return(Int(1))
        ]
    )

    check_admin = Cond(
        [And(
            Txn.application_args[1] == App.globalGet(Bytes("usertype")),
            Txn.application_args[2] == App.globalGet(Bytes("password"))
        ), Approve()]
    )

    group_transaction = Cond(
        [And(
            Global.group_size() == Int(2),
            Txn.application_args[0] == Bytes("check_admin")
        ), check_admin]
    )

    update_user = Seq(
        App.globalPut(Bytes("username"), Txn.application_args[0]),
        App.globalPut(Bytes("usertype"), Txn.application_args[1]),
        App.globalPut(Bytes("email"), Txn.application_args[2]),
        App.globalPut(Bytes("password"), Txn.application_args[3]),
        Approve()
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.NoOp, group_transaction],
        [Txn.on_completion() == OnComplete.UpdateApplication, update_user]
    )

    return program


if __name__ == "__main__":
    with open("admin_contract.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=5)
        f.write(compiled)