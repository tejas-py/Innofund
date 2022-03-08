import json
from API.connection import algo_conn
import utilities.CommonFunctions
from billiard.five import string
from algosdk.future import transaction
import os
import base64


def load_resource(res):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, res)
    with open(path, "rb") as fin:
        data = fin.read()
    return data


def transfer(creator_address):

    algod_client = algo_conn()

    creator = creator_address

    params = algod_client.suggested_params()

    myprogram = "D:\webmob\Innofund_new\escrow_account\sample.teal"

    data = load_resource(myprogram)
    source = data.decode('utf-8')
    response = algod_client.compile(source)
    programstr = response['result']
    t = programstr.encode("ascii")
    program = base64.decodebytes(t)
    lsig = transaction.LogicSigAccount(program)

    sender = lsig.address()

    receiver = creator

    txn = transaction.PaymentTxn(sender, params, receiver, 14444)

    #sign by logic sign
    lstx = transaction.LogicSigTransaction(txn, lsig)
    assert lstx.verify()
    txid = lstx.transaction.get_txid()
    print("Signed transaction with txID: {}".format(txid))

    algod_client.send_transaction(lstx)

    utilities.CommonFunctions.wait_for_confirmation(algod_client, txid)

    # Read the transction
    confirmed_txn = algod_client.pending_transaction_info(txid)
    print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4)))

    return string(txid)


