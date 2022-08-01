from algosdk.future import transaction
import utilities.CommonFunctions as com_func
from algosdk import account, mnemonic, encoding


# Declare application state storage (immutable)
local_ints = 0
local_bytes = 0
global_ints = 1
global_bytes = 1
global_schema = transaction.StateSchema(global_ints, global_bytes)
local_schema = transaction.StateSchema(local_ints, local_bytes)

# Declare approval program source
approval_program_source_initial = b"""#pragma version 5
txn ApplicationID
int 0
==
bnz main_l10
txn OnCompletion
int NoOp
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
global GroupSize
int 2
==
txna ApplicationArgs 0
byte "check_user"
==
&&
bnz main_l7
err
main_l7:
txna ApplicationArgs 1
byte "usertype"
app_global_get
==
bnz main_l9
err
main_l9:
int 1
return
main_l10:
txn NumAppArgs
int 1
==
assert
byte "usertype"
txna ApplicationArgs 0
app_global_put
int 1
return
"""


# Declare clear state program source
clear_program_source = b"""#pragma version 5
int 1
"""


# Generate a new admin account as well as new user id for each user that registers
def create_admin_account(client, usertype):
    print("Creating admin application...")

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
    on_complete = transaction.OnComplete.NoOpOC.real

    params = client.suggested_params()

    args_list = [bytes(usertype, 'utf8')]

    txn = transaction.ApplicationCreateTxn(sender, params, on_complete,
                                           approval_program, clear_program,
                                           global_schema, local_schema, args_list)

    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    client.send_transactions([signed_txn])
    com_func.wait_for_confirmation(client, tx_id)
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['application-index']

    return app_id


# update admin details on blockchain
def update_admin(client, public_address, admin_id, name, usertype, email):
    print("Updating existing admin....")

    approval_program = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)

    # declare sender
    sender = public_address

    # get node suggested parameters
    params = client.suggested_params()

    app_args = [bytes(name, 'utf8'), bytes(usertype, 'utf8'), bytes(email, 'utf8')]

    # create unsigned transaction
    txn = transaction.ApplicationUpdateTxn(sender, params, admin_id, approval_program, clear_program, app_args)

    txngrp = [{'txn':encoding.msgpack_encode (txn)}]

    return txngrp


# call user app and create asset
def admin_asset(client, usertype, admin_id, unit_name, asset_name, image_url, amt):

    # define address from private key of creator
    creator_account = com_func.get_address_from_application(admin_id)

    # set suggested params
    params = client.suggested_params()

    args = ["check_user", bytes(usertype, 'utf-8')]

    print("Calling user Application...")

    # admin to call app(admin): transaction 1
    sender = creator_account
    txn_1 = transaction.ApplicationNoOpTxn(sender, params, admin_id, args)
    params.fee = amt
    params.flat_fee = True

    print("Minting NFT...")

    # creating asset: transaction 2
    txn_2 = transaction.AssetConfigTxn(sender=sender, sp=params, total=10, default_frozen=False,
                                       unit_name=unit_name, asset_name=asset_name, decimals=1, url=image_url,
                                       manager=creator_account, freeze=creator_account, reserve=creator_account,
                                       clawback=creator_account)
    print("Grouping transactions...")
    # compute group id and put it into each transaction
    group_id = transaction.calculate_group_id([txn_1, txn_2])
    txn_1.group = group_id
    txn_2.group = group_id

    txngrp = [{'txn':encoding.msgpack_encode (txn_1)}, {'txn':encoding.msgpack_encode (txn_2)}]

    return txngrp
