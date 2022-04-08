from algosdk.future.transaction import *
from billiard.five import string
import utilities.CommonFunctions as com_func
from algosdk import mnemonic

approval_program_source_initial = b"""#pragma version 5
txn ApplicationID
int 0
==
bnz main_l4
txn OnCompletion
int UpdateApplication
==
bnz main_l3
err
main_l3:
byte "username"
txna ApplicationArgs 0
app_global_put
byte "usertype"
txna ApplicationArgs 1
app_global_put
byte "email"
txna ApplicationArgs 2
app_global_put
int 1
return
main_l4:
txn NumAppArgs
int 3
==
assert
byte "username"
txna ApplicationArgs 0
app_global_put
byte "usertype"
txna ApplicationArgs 1
app_global_put
byte "email"
txna ApplicationArgs 2
app_global_put
int 1
return
"""

# Declare clear state program source
clear_program_source = b"""#pragma version 5
int 1
"""


def update_user(client, user_passphrase, user_id, username, usertype, email):
    print("Updating existing user....")

    approval_program = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)

    # Converting Passphrase to public and private key.
    public_address = account.address_from_private_key(user_passphrase)
    private_key = mnemonic.to_private_key(user_passphrase)

    # declare sender
    sender = public_address

    # get node suggested parameters
    params = client.suggested_params()

    app_args = [bytes(username, 'utf8'), bytes(usertype, 'utf8'), bytes(email, 'utf8')]

    # create unsigned transaction
    txn = ApplicationUpdateTxn(sender, params, user_id, approval_program, clear_program, app_args)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation

    confirmed_txn = wait_for_confirmation(client, tx_id, 4)
    print("TXID: ", tx_id)
    print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))
    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['txn']['txn']['apid']

    return string(app_id)
