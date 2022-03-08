import json
from algosdk import mnemonic
from algosdk import transaction
from billiard.five import string

from API.connection import algo_conn
import utilities.CommonFunctions


def transfer(passphrase, amount):

    algod_client = algo_conn()

    #passphrase = "broken fossil rate oblige true always cost goddess hole rare novel autumn forest good corn price wolf together today advice abstract pulse live able always"

    private_key = mnemonic.to_private_key(passphrase)
    your_address = mnemonic.to_public_key(passphrase)
    print("My address: {}".format(your_address))

    account_info = algod_client.account_info(your_address)
    print("Account balance: {} microAlgos".format(account_info.get('amount')))

    params = algod_client.suggested_params()
    note = "Account to Escrow Account".encode()
    receiver = "BJATCHES5YJZJ7JITYMVLSSIQAVAWBQRVGPQUDT5AZ2QSLDSXWWM46THOY"

    txn = transaction.PaymentTxn(your_address, params.fee, params.first, params.last, params.gh, receiver, amount)
    signed_txn = txn.sign(private_key)
    txid = signed_txn.transaction.get_txid()
    print("Signed transaction with txID: {}".format(txid))

    algod_client.send_transaction(signed_txn)

    utilities.CommonFunctions.wait_for_confirmation(algod_client, txid)

    # Read the transction
    confirmed_txn = algod_client.pending_transaction_info(txid)
    print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4)))

    return string(txid)
