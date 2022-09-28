from pyteal import *


def donation_escrow(institutional_donor_wallet):

    return_payment = Seq(
        Assert(Txn.receiver() == Addr(institutional_donor_wallet)),
        Assert(Txn.fee() <= Int(1000)),
        Approve()
    )

    multi_transactions = Seq([
        # Txn_1
        Assert(Gtxn[0].application_id() == Btoi(Gtxn[0].application_args[3])),
        Assert(Gtxn[0].application_args[0] == Bytes("update_investment")),
        Assert(Gtxn[0].fee() <= Int(1000)),
        # Txn_2
        # Assert(Gtxn[1].receiver() == Gtxn[0].accounts[0]),
        Assert(Gtxn[1].amount() == Btoi(Gtxn[0].application_args[2])),
        Assert(Gtxn[1].fee() <= Int(1000)),
        Approve()
    ])

    program = Seq(
        Assert(Txn.rekey_to() == Global.zero_address()),
        Assert(Txn.close_remainder_to() == Global.zero_address()),
        Cond(
            # Condition 1
            [And(
                Global.group_size() == Int(2),
                Gtxn[0].type_enum() == TxnType.ApplicationCall,
                Gtxn[1].type_enum() == TxnType.Payment
            ), multi_transactions],
            # Condition 2
            [And(
                Global.group_size() == Int(1),
                Txn.type_enum() == TxnType.Payment,
            ), return_payment],
        )
    )

    return program
