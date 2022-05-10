# This transaction contains:
# 1. Create Account for new users (Create application transaction).
# 2. Update User(Creator and Investor) details (User update application transaction).
# 3. Delete existing user. (User application delete transaction)

from billiard.five import string
from algosdk.future.transaction import *
import utilities.CommonFunctions as com_func
from algosdk import account, mnemonic

# Declare application state storage (immutable)
local_ints = 5
local_bytes = 5
global_ints = 5
global_bytes = 5
global_schema = StateSchema(global_ints, global_bytes)
local_schema = StateSchema(local_ints, local_bytes)

# Declare approval program source
approval_program_source_initial = b"""#pragma version 5
txn ApplicationID
int 0
==
bnz main_l6
txn OnCompletion
int UpdateApplication
==
bnz main_l5
txn OnCompletion
int DeleteApplication
==
bnz main_l4
err
main_l4:
int 1
return
main_l5:
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
main_l6:
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


# Generate a new account as well as new user id for each user that registers
def create_app(client, username, usertype, email):
    print("Creating application...")

    approval_program = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)

    private_key, address = account.generate_account()
    print("Fund the address, use the link https://bank.testnet.algorand.network/ : {}".format(address))
    print("Here is your private key: \n{}".format(private_key))
    print("And this is your mnemonic: \n{}".format(mnemonic.from_private_key(private_key)))

    account_info = client.account_info(address)
    print("Account balance: {} microAlgos".format(account_info.get('amount')) + "\n")
    input("Press ENTER to continue...")

    sender = address
    on_complete = OnComplete.NoOpOC.real

    params = client.suggested_params()

    args_list = [bytes(username, 'utf8'), bytes(usertype, 'utf8'), bytes(email, 'utf8')]

    txn = ApplicationCreateTxn(sender, params, on_complete,
                               approval_program, clear_program,
                               global_schema, local_schema, args_list)

    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    client.send_transactions([signed_txn])
    com_func.wait_for_confirmation(client, tx_id)
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['application-index']
    print("Created new user id: ", app_id)

    return string(app_id)


# Update User(Creator and Investor) details (User update application transaction)
def update_user(client, user_passphrase, user_id, username, usertype, email):
    print("Updating existing user....")

    approval_program = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)

    # Converting Passphrase to public and private key.
    private_key = mnemonic.to_private_key(user_passphrase)
    public_address = account.address_from_private_key(private_key)

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


# delete the user
def delete_user(client, passphrase, user_id):

    print("Deleting {} user".format(user_id))
    # declare sender
    private_key = mnemonic.to_private_key(passphrase)
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()

    print("Doing Transaction...")
    # create unsigned transaction
    txn = ApplicationDeleteTxn(sender, params, user_id)

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