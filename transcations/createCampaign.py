from billiard.five import string
from algosdk.future import transaction
import utilities.CommonFunctions as com_func
from algosdk import account


# declare application state storage (immutable)
local_ints = 5
local_bytes = 5
global_ints = 5
global_bytes = 5
global_schema = transaction.StateSchema(global_ints, global_bytes)
local_schema = transaction.StateSchema(local_ints, local_bytes)


approval_program_source_initial = b"""#pragma version 5
txn ApplicationID
int 0
==
bnz main_l2
err
main_l2:
txn NumAppArgs
int 4
==
assert
byte "title"
txna ApplicationArgs 0
app_global_put
byte "description"
txna ApplicationArgs 1
app_global_put
byte "fund_limit"
txna ApplicationArgs 2
app_global_put
byte "duration"
txna ApplicationArgs 3
app_global_put
int 1
return
return
"""

# declare clear state program source
clear_program_source = b"""#pragma version 5
int 1
"""


# create new application
def create_app(client, title, description, fund_limit, duration):
    print("Creating application...")

    approval_program = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)

    private_key, address = account.generate_account()
    print("Fund the address, use the link https://bank.testnet.algorand.network/ : {}".format(address))

    account_info = client.account_info(address)
    print("Account balance: {} microAlgos".format(account_info.get('amount')) + "\n")
    input("Press ENTER to continue...")

    sender = address
    on_complete = transaction.OnComplete.NoOpOC.real

    params = client.suggested_params()

    params.flat_fee = True
    params.fee = 1000

    args_list = [bytes(title, 'utf8'), bytes(description, 'utf8'),bytes(fund_limit, 'utf8'), bytes(duration, 'utf8')]

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
