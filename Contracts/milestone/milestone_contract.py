from pyteal import *


def approval_program():

    on_creation = Seq(
        [
            Assert(Txn.application_args.length() == Int(3)),
            App.globalPut(Bytes("milestone_title"), Txn.application_args[0]),
            App.globalPut(Bytes("milestone_number"), Btoi(Txn.application_args[1])),
            App.globalPut(Bytes("end_time"), Btoi(Txn.application_args[2])),
            Return(Int(1))
        ]
    )

    start_check = Cond(
        [And(
            Txn.application_args[1] == App.globalGet(Bytes("milestone_title")),
            Btoi(Txn.application_args[2]) == App.globalGet(Bytes("milestone_number")),
            Btoi(Txn.application_args[3]) < App.globalGet(Bytes("end_time")),
        ), Approve()
        ]
    )

    end_check = Cond(
        [And(
            Btoi(Txn.application_args[1]) <= App.globalGet(Bytes("end_time")),
        ), Approve()
        ]
    )

    check_txn = Cond(
        [And(Global.group_size() == Int(2),
             Txn.application_args[0] == Bytes("start")), start_check
         ],
        [And(Global.group_size() == Int(1),
             Txn.application_args[0] == Bytes("end")), end_check
         ],
        [
          Txn.application_args[0] == Bytes('no_check'), Approve()
        ]
    )

    update_milestone = Seq(
        App.globalPut(Bytes("milestone_title"), Txn.application_args[1]),
        App.globalPut(Bytes("milestone_number"), Btoi(Txn.application_args[2])),
        App.globalPut(Bytes("end_time"), Btoi(Txn.application_args[3])),
        Approve()
    )

    check_txn_size = Cond(
        [And(
            Global.group_size() == Int(4),
            Txn.application_args[0] == Bytes("update_details")
        ), update_milestone]
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.NoOp, check_txn],
        [Txn.on_completion() == OnComplete.UpdateApplication, check_txn_size],
        [Txn.on_completion() == OnComplete.DeleteApplication, Approve()]
    )

    return program


if __name__ == "__main__":
    with open("milestone_contract.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=6)
        f.write(compiled)
