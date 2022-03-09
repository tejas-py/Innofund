from billiard.five import string
from algosdk.future import transaction
import utilities.CommonFunctions as com_func
from algosdk import mnemonic


# declare application state storage (immutable)
local_ints = 1
local_bytes = 1
global_ints = 20
global_bytes = 20
global_schema = transaction.StateSchema(global_ints, global_bytes)
local_schema = transaction.StateSchema(local_ints, local_bytes)


approval_program_source_initial = b"""#pragma version 5
txn ApplicationID
int 0
==
bnz main_l4
txn OnCompletion
int NoOp
==
bnz main_l3
err
main_l3:
int 0
return
main_l4:
txn NumAppArgs
int 8
==
assert
byte "title"
txna ApplicationArgs 0
app_global_put
byte "description"
txna ApplicationArgs 1
app_global_put
byte "category"
txna ApplicationArgs 2
app_global_put
byte "start_time"
txna ApplicationArgs 3
app_global_put
byte "end_time"
txna ApplicationArgs 4
app_global_put
byte "funding_category"
txna ApplicationArgs 5
app_global_put
byte "fund_limit"
txna ApplicationArgs 6
app_global_put
byte "country"
txna ApplicationArgs 7
app_global_put
int 1
return
"""

# declare clear state program source
clear_program_source = b"""#pragma version 5
int 1
"""


# create new application
def create_app(client, your_passphrase,  title, description,
               category, start_time, end_time, fund_category,
               fund_limit, country):
    print("Creating application...")

    approval_program = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)

    # Fetching public and private address from the passphrase, passed as argument.
    private_key = mnemonic.to_private_key(your_passphrase)
    address = mnemonic.to_public_key(your_passphrase)

    account_info = client.account_info(address)
    print("Account balance: {} microAlgos".format(account_info.get('amount')) + "\n")

    sender = address
    on_complete = transaction.OnComplete.NoOpOC.real

    params = client.suggested_params()

    params.flat_fee = True
    params.fee = 1000

    args_list = [bytes(title, 'utf8'), bytes(description, 'utf8'), bytes(category, 'utf8'),
                 bytes(start_time, 'utf8'), bytes(end_time, 'utf8'), bytes(fund_category, 'utf8'),
                 bytes(fund_limit, 'utf8'), bytes(country, 'utf8')]

    txn = transaction.ApplicationCreateTxn(sender, params, on_complete,
                                           approval_program, clear_program,
                                           global_schema, local_schema, args_list)

    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    client.send_transactions([signed_txn])
    com_func.wait_for_confirmation(client, tx_id)
    transaction_response = client.pending_transaction_info(tx_id)
    campaign_id = transaction_response['application-index']
    print("Created new Campaign ID: ", campaign_id)

    return string(campaign_id)
