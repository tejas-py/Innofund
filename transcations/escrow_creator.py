import json
import base64
from algosdk import mnemonic
from algosdk import transaction
from API.connection import algo_conn
import utilities.CommonFunctions


def transfer():

    algod_client = algo_conn()

    passphrase = "broken fossil rate oblige true always cost goddess hole rare novel autumn forest good corn price wolf together today advice abstract pulse live able always"

    private_key = mnemonic.to_private_key(passphrase)
    creator = mnemonic.to_public_key(passphrase)
    print("My address: {}".format(creator))

    account_info = algod_client.account_info(creator)
    print("Account balance: {} microAlgos".format(account_info.get('amount')))

    params = algod_client.suggested_params()
    note = "Account to Escrow Account".encode()
    sender = "BJATCHES5YJZJ7JITYMVLSSIQAVAWBQRVGPQUDT5AZ2QSLDSXWWM46THOY"

    escrow_private =

    receiver = creator

    txn = transaction.PaymentTxn(sender, params.fee, params.first, params.last, params.gh, receiver, 14444)
    signed_txn = txn.sign(private_key)
    txid = signed_txn.transaction.get_txid()
    print("Signed transaction with txID: {}".format(txid))

    algod_client.send_transaction(signed_txn)

    utilities.CommonFunctions.wait_for_confirmation(algod_client, txid)

    # Read the transction
    confirmed_txn = algod_client.pending_transaction_info(txid)
    print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4)))


transfer()
