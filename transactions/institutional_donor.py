import base64
from algosdk.future import transaction
from algosdk import encoding
from utilities import CommonFunctions
from API import connection


# logic sign
def logic_sig(client):

    # contract location
    myprogram = 'sub_escrow_account/sub_escrow_account.teal'

    data = CommonFunctions.load_resource(myprogram)
    response = client.compile(data.decode('utf-8'))
    program = base64.decodebytes(response['result'].encode("ascii"))

    arg1 = (123).to_bytes(8, 'big')
    lsig = transaction.LogicSigAccount(program, args=[arg1])

    return lsig


# transactions from institutional donor to sub-escrow account
def transfer_sub_escrow_account(client, campaign_investment, address, note):

    # define the total investment and sub-escrow account
    sub_escrow_account = logic_sig(client).address()
    total_investment = campaign_investment['fees']

    # find the total amount for investing
    for campaign_id in campaign_investment['investments']:
        investment = campaign_investment['investments'][campaign_id]
        total_investment += investment

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
    txn = transaction.PaymentTxn(sender=sub_escrow_account, sp=params, receiver=campaign_wallet_address, amt=amount, note=note)

    signed_txn = transaction.LogicSigTransaction(txn, logic_sig(client))

    tx_id = signed_txn.transaction.get_txid()
    client.send_transactions([signed_txn])
    CommonFunctions.wait_for_confirmation(client, tx_id)

    return tx_id
