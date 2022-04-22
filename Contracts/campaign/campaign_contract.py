from pyteal import *


def approval_program():

    time_check = Cond(
        [App.globalGet(Bytes("end_time")) > App.globalGet(Bytes("start_time")), Approve()]
    )

    on_creation = Seq(
        [
            Assert(Txn.application_args.length() == Int(10)),
            App.globalPut(Bytes("title"), Txn.application_args[0]),
            App.globalPut(Bytes("description"), Txn.application_args[1]),
            App.globalPut(Bytes("category"), Txn.application_args[2]),
            App.globalPut(Bytes("start_time"), Btoi(Txn.application_args[3])),
            App.globalPut(Bytes("end_time"), Btoi(Txn.application_args[4])),
            App.globalPut(Bytes("funding_category"), Txn.application_args[5]),
            App.globalPut(Bytes("fund_limit"), Btoi(Txn.application_args[6])),
            App.globalPut(Bytes("reward_type"), Txn.application_args[7]),
            App.globalPut(Bytes("country"), Txn.application_args[8]),
            App.globalPut(Bytes("total_investment"), Btoi(Txn.application_args[9])),
            time_check
        ]
    )

    check = Cond(
        [And(
            App.globalGet(Bytes("end_time")) > App.globalGet(Bytes("start_time")),
            Btoi(Txn.application_args[1]) <= App.globalGet(Bytes("fund_limit")),
            App.globalGet(Bytes("fund_limit")) >= App.globalGet(Bytes("total_investment"))
        ), Approve()
        ]
    )

    check_again = If(Btoi(Txn.application_args[1]) > App.globalGet(Bytes("end_time")), Approve(), Reject())

    group_transaction = Cond(
        [And(
            Global.group_size() == Int(2),
            Txn.application_args[0] == Bytes("Check")
        ), check],
        [And(
            Global.group_size() == Int(2),
            Txn.application_args[0] == Bytes("Check_again")
        ), check_again],
        [And(
            Global.group_size() == Int(4),
            Txn.application_args[0] == Bytes("No Check")
        ), Approve()],
    )

    update_investment_details = Seq(
        App.globalPut(Bytes("total_investment"), App.globalGet(Bytes("total_investment")) + Btoi(Txn.application_args[2]
                                                                                                 )),
        Approve()
    )

    investment_done_realtime = App.globalGet(Bytes("fund_limit")) - App.globalGet(Bytes("total_investment"))

    check_investment_details = Cond(
        [And(
            Btoi(Txn.application_args[2]) <= investment_done_realtime,
            App.globalGet(Bytes("end_time")) > Btoi(Txn.application_args[1])
        ), update_investment_details]
    )

    check_updated_time = Cond(
        [App.globalGet(Bytes("end_time")) > App.globalGet(Bytes("start_time")), Approve()]
    )

    update_campaign_details = Seq(
        App.globalPut(Bytes("title"), Txn.application_args[1]),
        App.globalPut(Bytes("description"), Txn.application_args[2]),
        App.globalPut(Bytes("category"), Txn.application_args[3]),
        App.globalPut(Bytes("start_time"), Btoi(Txn.application_args[4])),
        App.globalPut(Bytes("end_time"), Btoi(Txn.application_args[5])),
        App.globalPut(Bytes("funding_category"), Txn.application_args[6]),
        App.globalPut(Bytes("fund_limit"), Btoi(Txn.application_args[7])),
        App.globalPut(Bytes("reward_type"), Txn.application_args[8]),
        App.globalPut(Bytes("country"), Txn.application_args[9]),
        check_updated_time
    )

    update_campaign = Cond(
        [Txn.application_args[0] == Bytes("update_investment"), check_investment_details],
        [Txn.application_args[0] == Bytes("update_details"), update_campaign_details]
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.NoOp, group_transaction],
        [Txn.on_completion() == OnComplete.UpdateApplication, update_campaign],
        [Txn.on_completion() == OnComplete.DeleteApplication, Approve()]
    )

    return program


if __name__ == "__main__":
    with open("campaign_contract.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=5)
        f.write(compiled)

