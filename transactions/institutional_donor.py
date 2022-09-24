import base64
from algosdk.future import transaction
from algosdk import encoding
from utilities import CommonFunctions


# logic sign
def logic_sig(client):
    # contract location
    myprogram = 'sub_escrow_account/sub_escrow_account.teal'

    data = CommonFunctions.load_resource(myprogram)
    response = client.compile(data.decode('utf-8'))
    program = base64.decodebytes(response['result'].encode("ascii"))

    arg1 = bytes("Donation to Campaign", 'utf-8')
    lsig = transaction.LogicSigAccount(program, args=[arg1])

    return lsig


# transactions from institutional donor to sub-escrow account
def transfer_sub_escrow_account(client, total_investment, address, note):

    # define the total investment and sub-escrow account
    sub_escrow_account = logic_sig(client).address()

    # get node suggested parameters
    params = client.suggested_params()

    # payment transaction
    txn = transaction.PaymentTxn(sender=address, sp=params, receiver=sub_escrow_account, amt=total_investment, note=note)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# investment from escrow account to campaign
def escrow_campaign(client, campaign_app_id, amount, note):

    # get node suggested parameters
    params = client.suggested_params()

    # address of sub_escrow_account
    sub_escrow_account = logic_sig(client).address()

    # campaign app id address
    campaign_wallet_address = encoding.encode_address(encoding.checksum(b'appID' + campaign_app_id.to_bytes(8, 'big')))

    # payment transaction
    app_args = ["update_investment", int(CommonFunctions.Today_seconds()), int(amount)]
    txn_1 = transaction.ApplicationNoOpTxn(sub_escrow_account, params, campaign_app_id, app_args)
    txn_2 = transaction.PaymentTxn(sender=sub_escrow_account, sp=params, receiver=campaign_wallet_address, amt=amount, note=note)

    print("Grouping transactions...")
    # compute group id and put it into each transaction
    group_id = transaction.calculate_group_id([txn_1, txn_2])
    print("groupID of the Transaction: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id

    # sign transactions
    print("Signing transactions...")

    stxn_1 = transaction.LogicSigTransaction(txn_1, logic_sig(client))
    print("Investor signed txn_1: ", stxn_1.get_txid())

    stxn_2 = transaction.LogicSigTransaction(txn_2, logic_sig(client))
    print("Investor signed txn_2: ", stxn_2.get_txid())
    payment_transaction_id = stxn_2.get_txid()

    # assemble transaction group
    print("Assembling transaction group...")
    signedGroup = [stxn_1, stxn_2]

    # send transactions
    print("Sending transaction group...")
    tx_id = client.send_transactions(signedGroup)

    # wait for confirmation
    CommonFunctions.wait_for_confirmation(client, tx_id)

    return str(payment_transaction_id)
