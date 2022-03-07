import json
import base64
from algosdk import mnemonic
from algosdk import transaction
from est_connection import algo_conn


# utility for waiting on a transaction confirmation
def wait_for_confirmation(algod_client, txid):
    last_round = algod_client.status().get('last-round')
    txinfo = algod_client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation...")
        last_round += 1
        algod_client.status_after_block(last_round)
        txinfo = algod_client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo


def transfer():

    algod_client = algo_conn()

    passphrase = "broken fossil rate oblige true always cost goddess hole rare novel autumn forest good corn price wolf together today advice abstract pulse live able always"

    private_key = mnemonic.to_private_key(passphrase)
    my_address = mnemonic.to_public_key(passphrase)
    print("My address: {}".format(my_address))

    account_info = algod_client.account_info(my_address)
    print("Account balance: {} microAlgos".format(account_info.get('amount')))

    params = algod_client.suggested_params()
    note = "Test Transfer".encode()
    receiver = "XNEERDAOF6VV2KVG3622KUN4HHNB2UMUYMZQ2XHC7TT5HCGEPEMZEXY7FI"

    txn = transaction.PaymentTxn(my_address,params.fee,params.first,params.last,params.gh,receiver,1000000)
    signed_txn = txn.sign(private_key)
    txid = signed_txn.transaction.get_txid()
    print("Signed transaction with txID: {}".format(txid))

    algod_client.send_transaction(signed_txn)

    # wait for confirmation
    wait_for_confirmation(algod_client, txid)

    # Read the transction
    confirmed_txn = algod_client.pending_transaction_info(txid)
    print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4)))
    print("Decoded note: {}".format(base64.b64decode(confirmed_txn.get('noteb64')).decode()))


transfer()

