from pyteal import *


def approval_program():

    # Define Variables
    account_number = ScratchVar(TealType.uint64)
    repayment_number = ScratchVar(TealType.uint64)

    # Checks that the sender is the app creator
    is_app_creator = Txn.sender() == Global.creator_address()

    time_check = Cond(
        # Condition 1
        [App.globalGet(Bytes("end_time")) > App.globalGet(Bytes("start_time")), Approve()]
    )

    # Constructor
    on_creation = Seq(
        [
            Assert(Txn.application_args.length() == Int(9)),
            App.globalPut(Bytes("title"), Txn.application_args[0]),
            App.globalPut(Bytes("category"), Txn.application_args[1]),
            App.globalPut(Bytes("end_time"), Btoi(Txn.application_args[2])),
            App.globalPut(Bytes("funding_category"), Txn.application_args[3]),
            App.globalPut(Bytes("fund_limit"), Btoi(Txn.application_args[4])),
            App.globalPut(Bytes("reward_type"), Txn.application_args[5]),
            App.globalPut(Bytes("country"), Txn.application_args[6]),
            App.globalPut(Bytes("total_investment"), Btoi(Txn.application_args[7])),
            App.globalPut(Bytes("ESG"), Btoi(Txn.application_args[8])),
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
            TxnField.asset_amount: Int(10),
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
            TxnField.type_enum: TxnType.Payment,
            TxnField.sender: Global.current_application_address(),
            TxnField.receiver: Txn.accounts[1],
            TxnField.amount: Btoi(Txn.application_args[2]),
            TxnField.fee: Int(0)
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        Approve()
    )

    inner_txn6 = Seq(
        InnerTxnBuilder.Begin(),
        # Transaction: payment to creator for milestone
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.sender: Global.current_application_address(),
            TxnField.receiver: Txn.accounts[1],
            TxnField.close_remainder_to: Txn.accounts[1],
            TxnField.fee: Int(0)
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        Approve()
    )

    inner_txn5 = Seq(
        InnerTxnBuilder.Begin(),
        # Transaction: close out asset in the smart contract
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.asset_receiver: Txn.accounts[1],
            TxnField.asset_close_to: Txn.accounts[1],
            TxnField.asset_amount: Int(0),
            TxnField.xfer_asset: Txn.assets[0],
            TxnField.fee: Int(0)
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        inner_txn6
    )

    # multiple repayment to investors when milestone gets rejected
    inner_txn7 = Seq([
        account_number.store(Int(1)),
        For(repayment_number.store(Int(3)), repayment_number.load() < Btoi(Txn.application_args[2]), repayment_number.store(repayment_number.load() + Int(1))).Do(
            InnerTxnBuilder.Begin(),
            # Transaction: payment to creator for milestone
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.Payment,
                TxnField.sender: Global.current_application_address(),
                TxnField.receiver: Txn.accounts[account_number.load()],
                TxnField.amount: Btoi(Txn.application_args[repayment_number.load()]),
                TxnField.fee: Int(0)
            }),
            # Submit the transaction
            InnerTxnBuilder.Submit(),
            # Increment Account number
            account_number.store(account_number.load() + Int(1))
        ),
        Approve()
    ])

    block_campaign_cond = Cond(
        [Txn.application_args[0] == Bytes("Block Reward Campaign"), inner_txn3],
        [Txn.application_args[0] == Bytes("Block Campaign"), Approve()],
    )

    # blocking running campaign
    inner_txn8 = Seq([
        account_number.store(Int(1)),
        For(repayment_number.store(Int(2)), repayment_number.load() < Btoi(Txn.application_args[1]), repayment_number.store(repayment_number.load() + Int(1))).Do(
            InnerTxnBuilder.Begin(),
            # Transaction: payment to creator for milestone
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.Payment,
                TxnField.sender: Global.current_application_address(),
                TxnField.receiver: Txn.accounts[account_number.load()],
                TxnField.amount: Btoi(Txn.application_args[repayment_number.load()]),
                TxnField.fee: Int(0)
            }),
            # Submit the transaction
            InnerTxnBuilder.Submit(),
            # Increment Account number
            account_number.store(account_number.load() + Int(1))
        ),
        block_campaign_cond,
    ])

    multiple_conditions = Cond(
        [Txn.application_args[0] == Bytes("Check if the campaign has ended."), Approve()],
        [Txn.application_args[0] == Bytes("Claim NFT"), inner_txn2],
        [Txn.application_args[0] == Bytes("Milestone"), inner_txn4],
        [Txn.application_args[0] == Bytes("End Reward Milestone"), inner_txn5],
        [Txn.application_args[0] == Bytes("last_milestone"), inner_txn6],
        [Txn.application_args[0] == Bytes("return payment to investors, milestone rejected"), inner_txn7]
    )

    check_campaign_end = If(
        Or(
            Btoi(Txn.application_args[1]) > App.globalGet(Bytes("end_time")),
            App.globalGet(Bytes("fund_limit")) == App.globalGet(Bytes("total_investment"))
        ), multiple_conditions, Reject())

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
            Global.group_size() == Int(4),
            Txn.application_args[0] == Bytes('delete campaign')
        ), Approve()],
        # Condition 5
        [And(
            Global.group_size() == Int(3),
            is_app_creator,
            Txn.application_args[0] == Bytes("Send NFT to Campaign")
        ), inner_txn1],
        # Condition 6
        [And(
            Global.group_size() == Int(2),
            Txn.application_args[0] == Bytes("Claim NFT")
        ), check_campaign_end],
        # Condition 7
        [And(
            Global.group_size() == Int(4),
            is_app_creator,
            Txn.application_args[0] == Bytes("Transfer NFT to Creator")
        ), inner_txn3],
        # Condition 8
        [Txn.application_args[0] == Bytes("Milestone"), check_campaign_end],
        # Condition 9
        [Txn.application_args[0] == Bytes("End Reward Milestone"), check_campaign_end],
        # Condition 10
        [Txn.application_args[0] == Bytes("last_milestone"), check_campaign_end],
        # Condition 11
        [Txn.application_args[0] == Bytes("return payment to investors, milestone rejected"), check_campaign_end],
        # Condition 12
        [Txn.application_args[0] == Bytes("Block Reward Campaign"), inner_txn8],
        #  Condition 13
        [Txn.application_args[0] == Bytes("Block Campaign"), inner_txn8],
    )

    update_investment_details = Seq(
        App.globalPut(
            Bytes("total_investment"), App.globalGet(Bytes("total_investment")) + Btoi(Txn.application_args[2])
        ),
        Approve()
    )

    investment_done_realtime = App.globalGet(Bytes("fund_limit")) - App.globalGet(Bytes("total_investment"))

    check_investment_details = Cond(
        # Condition 1
        [And(
            Btoi(Txn.application_args[2]) <= investment_done_realtime,
            App.globalGet(Bytes("end_time")) > Btoi(Txn.application_args[1])
        ), update_investment_details]
    )

    update_campaign_details = Seq(
        [
            App.globalPut(Bytes("title"), Txn.application_args[1]),
            App.globalPut(Bytes("category"), Txn.application_args[2]),
            App.globalPut(Bytes("end_time"), Btoi(Txn.application_args[3])),
            App.globalPut(Bytes("funding_category"), Txn.application_args[4]),
            App.globalPut(Bytes("fund_limit"), Btoi(Txn.application_args[5])),
            App.globalPut(Bytes("country"), Txn.application_args[6]),
            Approve()
        ]
    )

    update_esg = Seq(
        App.globalPut(Bytes("ESG"), Txn.application_args[1]),
        Approve()
    )

    update_campaign = Cond(
        # Condition 1
        [And(
            Global.group_size() == Int(2),
            Txn.application_args[0] == Bytes("update_investment")
        ), check_investment_details],
        # Condition 2
        [And(
            Global.group_size() == Int(3),
            Txn.application_args[0] == Bytes("update_details")
        ), update_campaign_details],
        # Condition 3
        [Txn.application_args[0] == Bytes("update_ESG"), update_esg]
    )

    program = Cond(
        # Condition 1
        [Txn.application_id() == Int(0), on_creation],
        # Condition 2
        [Txn.on_completion() == OnComplete.NoOp, group_transaction],
        # Condition 3
        [Txn.on_completion() == OnComplete.UpdateApplication, update_campaign],
        # Condition 4
        [Txn.on_completion() == OnComplete.DeleteApplication, Approve()]
    )

    return program


if __name__ == "__main__":
    with open("campaign_contract.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=6)
        f.write(compiled)
