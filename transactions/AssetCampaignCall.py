# This transaction contains:
# 1. Group transaction of (Campaign App call and burn asset by campaign creator)

from algosdk.future import transaction
from algosdk import account, mnemonic
from billiard.five import string
import utilities.CommonFunctions as com_func


# Group transaction: (Campaign app call and Burn Asset)
def call_asset_destroy(client, creator_passphrase, asset_id, campaignID):

    # define address from private key of creator
    creator_private_key = mnemonic.to_private_key(creator_passphrase)
    creator_account = account.address_from_private_key(creator_private_key)

    # set suggested params
    params = client.suggested_params()

    args = ["No Check"]

    print("Calling Campaign Application...")

    # creator to call app(campaign): transaction 1
    sender = creator_account
    txn_1 = transaction.ApplicationNoOpTxn(sender, params, campaignID, args)
    print("Created Transaction 1: ", txn_1.get_txid())

    # destroying asset: transaction 2
    txn_2 = transaction.AssetConfigTxn(sender=sender, sp=params, index=asset_id, strict_empty_address_check=False)
    print("Created Transaction 2: ", txn_2.get_txid())

    # grouping both the txn to give the group id
    print("Grouping Transactions...")
    group_id = transaction.calculate_group_id([txn_1, txn_2])
    print("groupID of the Transaction: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id

    # split transaction group
    print("Splitting unsigned transaction group...")

    # signing the transactions
    stxn_1 = txn_1.sign(creator_private_key)
    print("Investor signed txn_1: ", stxn_1.get_txid())

    stxn_2 = txn_2.sign(creator_private_key)
    print("Investor signed txn_2: ", stxn_2.get_txid())

    # grouping the sign transactions
    signedGroup = [stxn_1, stxn_2]

    # send transactions
    print("Sending transaction group...")
    tx_id = client.send_transactions(signedGroup)

    # wait for confirmation
    com_func.wait_for_confirmation(client, tx_id)

    return string(tx_id)
