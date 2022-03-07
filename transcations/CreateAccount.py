from billiard.five import string
from pyteal import *
import base64

from algosdk.future import transaction
from algosdk import account, mnemonic
from algosdk.v2client import algod
import utilities.CommonFunctions as com_func
import API.connection

# declare application state storage (immutable)
local_ints = 5
local_bytes = 5
global_ints = 5
global_bytes = 5
global_schema = transaction.StateSchema(global_ints, global_bytes)
local_schema = transaction.StateSchema(local_ints, local_bytes)


approval_program_source_initial = b"""#pragma version 2
txn ApplicationID
int 0
==
bnz main_l2
err
main_l2:
txn NumAppArgs
int 4
==
bnz main_l4
err
main_l4:
byte "name"
txna ApplicationArgs 0
app_global_put
byte "usertype"
txna ApplicationArgs 1
app_global_put
byte "email"
txna ApplicationArgs 2
app_global_put
byte "password"
txna ApplicationArgs 3
app_global_put
int 1
return
"""

# declare clear state program source
clear_program_source = b"""#pragma version 5
int 1
"""


# create new application
def create_app(client, private_key, name, usertype, email, password):
    print("Creating application...")

    approval_program = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)

    sender = account.address_from_private_key(private_key)
    on_complete = transaction.OnComplete.NoOpOC.real

    params = client.suggested_params()

    params.flat_fee = True
    params.fee = 1000

    args_list = [bytes(name, 'utf8'), bytes(usertype, 'utf8'),bytes(email, 'utf8'), bytes(password, 'utf8')]

    txn = transaction.ApplicationCreateTxn(sender, params, on_complete,
                                           approval_program, clear_program,
                                           global_schema, local_schema, args_list)
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    client.send_transactions([signed_txn])
    com_func.wait_for_confirmation(client, tx_id)
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['application-index']
    print("Created new app-id: ", app_id)

    return string(app_id)
