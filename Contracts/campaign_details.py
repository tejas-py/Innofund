from pyteal import *


def approval_program():
    on_creation = Seq(
        [
            Assert(Txn.application_args.length() == Int(6)),
            App.globalPut(Bytes("creator"), Txn.application_args[0]),
            App.globalPut(Bytes("title"), Txn.application_args[1]),
            App.globalPut(Bytes("campaign_type"), Txn.application_args[2]),
            App.globalPut(Bytes("description"), Txn.application_args[3]),
            App.globalPut(Bytes("start_time"), Txn.application_args[4]),
            App.globalPut(Bytes("end_time"), Txn.application_args[5]),
            App.globalPut(Bytes("fund_limit"), Txn.application_args[6]),
            Return(Int(1))
        ]
    )
    program = Cond(
        [Txn.application_id() == Int(0), on_creation]
    )

    return program


if __name__ == "__main__":
    with open("campaign_details.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=5)
        f.write(compiled)
