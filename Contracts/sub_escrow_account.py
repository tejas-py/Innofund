from pyteal import *


def donation_escrow(campaign_app_id, campaign_wallet_address, institutional_donor_wallet):

    return_payment = Seq([
        Assert(Txn.type_enum() == TxnType.Payment),
        Assert(Txn.receiver == Txn.accounts[institutional_donor_wallet]),
        Assert(Txn.fee == Int(1000)),
        Approve()
    ])

    multi_transactions = Seq([
        # Txn_1
        Assert(Gtxn[0].type_enum() == TxnType.ApplicationCall),
        Assert(Gtxn[0].application_id() == Int(campaign_app_id)),
        Assert(Gtxn[0].application_args[0] == Bytes("update_investment")),
        # Txn_2
        Assert(Gtxn[1].type_enum() == TxnType.Payment),
        Assert(Gtxn[1].receiver() == campaign_wallet_address),
        Assert(Gtxn[1].amount() == Gtxn[0].application_args[2]),
        Assert(Txn.fee() <= Int(2000)),
        Approve()
    ])

    program = Cond(
        # Condition 1
        [And(
            Global.group_size() == Int(2),
            Txn.application_args[0] == Bytes("Donation to Campaign")
        ), multi_transactions],
        # Condition 2
        [Txn.application_args[0] == Bytes("Donation payment failed, Return payment to donors"), return_payment],
    )

    return program
