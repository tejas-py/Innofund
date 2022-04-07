from algosdk.future import transaction
from algosdk import account
from billiard.five import string
import utilities.CommonFunctions as com_func


# creator create asset and calling campaign id
def call_asset(client, private_key, campaignID, total_nft, unit_name, asset_name, file_path):
    # define address from private key of creator
    creator_account = account.address_from_private_key(private_key)
    creator_private_key = private_key

    # set suggested params
    params = client.suggested_params()

    args = ["No Check"]

    print("Calling Campaign Application...")

    # creator to call app(campaign): transaction 1
    sender = creator_account
    txn_1 = transaction.ApplicationNoOpTxn(sender, params, campaignID, args)
    print("Created Transaction 1: ", txn_1.get_txid())

    # creating asset: transaction 2
    txn_2 = transaction.AssetConfigTxn(sender=sender, sp=params, total=total_nft, default_frozen=False,
                                       unit_name=unit_name, asset_name=asset_name, manager=creator_account,
                                       reserve=creator_account, freeze=creator_account, clawback=creator_account,
                                       url=file_path, decimals=0)

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


# Creator destroy asset and call app.
def call_asset_destroy(client, private_key, asset_id, campaignID):
    # define address from private key of creator
    creator_account = account.address_from_private_key(private_key)
    creator_private_key = private_key

    # set suggested params
    params = client.suggested_params()

    args = ["No Check"]

    print("Calling Campaign Application...")

    # creator to call app(campaign): transaction 1
    sender = creator_account
    txn_1 = transaction.ApplicationNoOpTxn(sender, params, campaignID, args)
    print("Created Transaction 1: ", txn_1.get_txid())

    # creating asset: transaction 2
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
