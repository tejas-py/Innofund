from pyteal import *


def approval_program():

    on_creation = Seq(
        [
            Assert(Txn.application_args.length() == Int(1)),
            App.globalPut(Bytes("usertype"), Txn.application_args[0]),
            Return(Int(1))
        ]
    )

    inner_txn1 = Seq(
        InnerTxnBuilder.Begin(),
        # Transaction: NFT Transfer to admin
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.asset_receiver: Txn.accounts[0],
            TxnField.asset_amount: Int(1),
            TxnField.xfer_asset: Txn.assets[0],
            TxnField.fee: Int(0),
            TxnField.note: Bytes('NFT withdraw from Cashdillo Marketplace')
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        Approve()
    )

    inner_txn2 = Seq(
        InnerTxnBuilder.Begin(),
        # Transaction: NFT Transfer to creator
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.asset_receiver: Txn.accounts[1],
            TxnField.asset_amount: Int(1),
            TxnField.xfer_asset: Txn.assets[0],
            TxnField.fee: Int(0),
            TxnField.note: Bytes('NFT bought from Cashdillo Marketplace')
        }),
        # Submit the transaction
        InnerTxnBuilder.Submit(),
        Approve()
    )

    # optin nft
    inner_txn3 = Seq(
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

    group_transaction = Cond(
        [Txn.application_args[0] == Bytes('Withdraw NFT'), inner_txn1],
        [And(
            Global.group_size() == Int(3),
            Txn.application_args[0] == Bytes('Add NFT')
        ), inner_txn3],
        [And(
            Global.group_size() == Int(3),
            Txn.application_args[0] == Bytes('Buy NFT')
        ), inner_txn2],
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.NoOp, group_transaction],
        [Txn.on_completion() == OnComplete.DeleteApplication, Approve()]
    )

    return program


# ClearState Program
def clearstate_contract():
    return Approve()
