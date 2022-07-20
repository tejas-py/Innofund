from pyteal import *


def approval_program():

    # Checks that the sender is the app creator
    is_app_creator = Txn.sender() == Global.creator_address()

    time_check = Cond(
        [App.globalGet(Bytes("end_time")) > App.globalGet(Bytes("start_time")), Approve()]
    )

    on_creation = Seq(
        [
            Assert(Txn.application_args.length() == Int(8)),
            App.globalPut(Bytes("title"), Txn.application_args[0]),
            App.globalPut(Bytes("category"), Txn.application_args[1]),
            App.globalPut(Bytes("end_time"), Btoi(Txn.application_args[2])),
            App.globalPut(Bytes("funding_category"), Txn.application_args[3]),
            App.globalPut(Bytes("fund_limit"), Btoi(Txn.application_args[4])),
            App.globalPut(Bytes("reward_type"), Txn.application_args[5]),
            App.globalPut(Bytes("country"), Txn.application_args[6]),
            App.globalPut(Bytes("total_investment"), Btoi(Txn.application_args[7])),
            time_check
        ]
    )

    inner_txn1 = Seq(
        InnerTxnBuilder.Begin(),
        # Transaction: Opt-in NFT
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.asset_receiver: Global.current_application_address(),
            TxnField.asset_amount: Int(0),
            TxnField.xfer_asset: Txn.assets[0],
            TxnField.fee: Int(0)
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        Approve()
    )

    inner_txn2 = Seq(
        InnerTxnBuilder.Begin(),
        # Transaction: NFT Transfer to investor
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.asset_receiver: Txn.sender(),
            TxnField.asset_amount: Btoi(Txn.application_args[2]),
            TxnField.xfer_asset: Txn.assets[0],
            TxnField.fee: Int(0)
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        Approve()
    )

    inner_txn3 = Seq(
        InnerTxnBuilder.Begin(),
        # Transaction: NFT Transfer to creator
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.asset_receiver: Txn.accounts[0],
            TxnField.asset_amount: Int(1),
            TxnField.xfer_asset: Txn.assets[0],
            TxnField.fee: Int(0)
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        Approve()
    )

    inner_txn4 = Seq(
        InnerTxnBuilder.Begin(),
        # Transaction: payment to creator for milestone
        InnerTxnBuilder.SetFields({
            TxnField.type_enum:TxnType.Payment,
            TxnField.sender: Global.current_application_address(),
            TxnField.receiver: Txn.accounts[1],
            TxnField.amount: Btoi(Txn.application_args[2]),
            TxnField.fee: Int(0)
        }),

        # Submit the transaction
        InnerTxnBuilder.Submit(),
        Approve()
    )

    inner_txn5 = Seq(
        InnerTxnBuilder.Begin(),
        # Transaction: payment to creator for milestone
        InnerTxnBuilder.SetFields({
            TxnField.type_enum:TxnType.Payment,
            TxnField.sender: Global.current_application_address(),
            TxnField.receiver: Txn.accounts[1],
            TxnField.close_remainder_to: Txn.accounts[1],
            TxnField.fee: Int(0)
        }),

        # Submit the transaction
        InnerTxnBuilder.Submit(),
        Approve()
    )


    check_campaign_end = If(
        Or(
            Btoi(Txn.application_args[1]) > App.globalGet(Bytes("end_time")),
            App.globalGet(Bytes("fund_limit")) == App.globalGet(Bytes("total_investment"))
        ), Approve(), Reject())


    check_campaign_end_2 = If(
        Or(
            Btoi(Txn.application_args[1]) > App.globalGet(Bytes("end_time")),
            App.globalGet(Bytes("fund_limit")) == App.globalGet(Bytes("total_investment"))
        ), inner_txn2, Reject())

    # check_campaign_end_3 = If(
    #     Or(
    #         Btoi(Txn.application_args[1]) > App.globalGet(Bytes("end_time")),
    #         App.globalGet(Bytes("fund_limit")) == App.globalGet(Bytes("total_investment"))
    #     ), inner_txn3, Reject())

    check_campaign_end_4 = If(
        Or(
            Btoi(Txn.application_args[1]) > App.globalGet(Bytes("end_time")),
            App.globalGet(Bytes("fund_limit")) == App.globalGet(Bytes("total_investment"))
        ), inner_txn4, Reject())

    check_campaign_end_5 = If(
        Or(
            Btoi(Txn.application_args[1]) > App.globalGet(Bytes("end_time")),
            App.globalGet(Bytes("fund_limit")) == App.globalGet(Bytes("total_investment"))
        ), inner_txn5, Reject())


    group_transaction = Cond(

        # Condition 1
        [And(
            Global.group_size() == Int(2),
            Txn.application_args[0] == Bytes("Check if the campaign has ended.")
        ), check_campaign_end],

        # Condition 2
        [Txn.application_args[0] == Bytes("No Check"), Approve()],

        # Condition 3
        [Txn.application_args[0] == Bytes("Reject Reward Campaign"), inner_txn3],

        # Condition 4
        [And(
            Global.group_size() == Int(3),
            is_app_creator,
            Txn.application_args[0] == Bytes("Send NFT to Campaign")
        ), inner_txn1],

        # Condition 5
        [And(
            Global.group_size() == Int(2),
            Txn.application_args[0] == Bytes("Claim NFT")
        ), check_campaign_end_2],

        # Condition 6
        [And(
            Global.group_size() == Int(4),
            is_app_creator,
            Txn.application_args[0] == Bytes("Transfer NFT to Creator")
        ), inner_txn3],

        # Condition 7
        [Txn.application_args[0] == Bytes("Milestone"), check_campaign_end_4],

        # Condition 8
        [Txn.application_args[0] == Bytes("last_milestone"), check_campaign_end_5]
    )

    update_investment_details = Seq(
        App.globalPut(Bytes("total_investment"),
            App.globalGet(Bytes("total_investment")) + Btoi(Txn.application_args[2])
        ),
        Approve()
    )

    investment_done_realtime = App.globalGet(Bytes("fund_limit")) - App.globalGet(Bytes("total_investment"))

    check_investment_details = Cond(
        [And(
            Btoi(Txn.application_args[2]) <= investment_done_realtime,
            App.globalGet(Bytes("end_time")) > Btoi(Txn.application_args[1])
        ), update_investment_details]
    )

    update_campaign_details = Seq(
        App.globalPut(Bytes("title"), Txn.application_args[1]),
        App.globalPut(Bytes("category"), Txn.application_args[2]),
        App.globalPut(Bytes("end_time"), Btoi(Txn.application_args[3])),
        App.globalPut(Bytes("funding_category"), Txn.application_args[4]),
        App.globalPut(Bytes("fund_limit"), Btoi(Txn.application_args[5])),
        App.globalPut(Bytes("country"), Txn.application_args[6]),
        Approve()
    )

    update_campaign = Cond(
        [And(
            Global.group_size() == Int(2),
            Txn.application_args[0] == Bytes("update_investment")
        ), check_investment_details],
        [And(
            Global.group_size() == Int(3),
            Txn.application_args[0] == Bytes("update_details")
        ), update_campaign_details]
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
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=6)
        f.write(compiled)
