from pyteal import *
import base64

from algosdk.future import transaction
from algosdk import account, mnemonic
from algosdk.v2client import algod
import utilities.CommonFunctions as com_func

# user declared account mnemonics
creator_mnemonic = "recipe insane demand stem tube pulp discover auction amateur dove curtain club negative boil provide help economy name congress pave nothing color feel abandon lumber"
user_mnemonic = "brass unaware company mirror rail oil step journey cargo denial inflict code ozone route recall animal ribbon comfort expect fun liquid woman stone able arrest"

# declare application state storage (immutable)
local_ints = 1
local_bytes = 1
global_ints = 1
global_bytes = 0
global_schema = transaction.StateSchema(global_ints, global_bytes)
local_schema = transaction.StateSchema(local_ints, local_bytes)

approval_program_source_initial = b"""#pragma version 2
int 1
"""

# declare clear state program source
clear_program_source = b"""#pragma version 2
int 1
"""


# create new application
def create_app(client, private_key):
    print("Creating application...")

    creator_private_key = com_func.get_private_key_from_mnemonic(creator_mnemonic)
    user_private_key = com_func.get_private_key_from_mnemonic(user_mnemonic)

    approval_program = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)

    sender = account.address_from_private_key(private_key)
    on_complete = transaction.OnComplete.NoOpOC.real

    params = client.suggested_params()

    params.flat_fee = True
    params.fee = 1000

    txn = transaction.ApplicationCreateTxn(sender, params, on_complete,
                                           approval_program, clear_program,
                                           global_schema, local_schema)
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    client.send_transactions([signed_txn])
    com_func.wait_for_confirmation(client, tx_id)
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['application-index']
    print("Created new app-id: ", app_id)

    return app_id
