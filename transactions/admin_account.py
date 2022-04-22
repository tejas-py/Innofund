# This transaction contains:
# 1. creation of admin account
# 2. update admin account details
# 3. group transaction: (Admin Call app and minting NFT by the admin)

from billiard.five import string
from algosdk.future import transaction
import utilities.CommonFunctions as com_func
from algosdk import account, mnemonic


# Declare application state storage (immutable)
local_ints = 1
local_bytes = 1
global_ints = 10
global_bytes = 10
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
int UpdateApplication
==
bnz main_l4
err
main_l4:
byte "username"
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
main_l5:
global GroupSize
int 2
==
txna ApplicationArgs 0
byte "check_admin"
==
&&
bnz main_l7
err
main_l7:
txna ApplicationArgs 1
byte "usertype"
app_global_get
==
txna ApplicationArgs 2
byte "password"
app_global_get
==
&&
bnz main_l9
err
main_l9:
int 1
return
main_l10:
txn NumAppArgs
int 4
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
byte "password"
txna ApplicationArgs 3
app_global_put
int 1
return
"""


# Declare clear state program source
clear_program_source = b"""#pragma version 5
int 1
"""


# Generate a new admin account as well as new user id for each user that registers
def create_admin_account(client, username, usertype, email, password):
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
    on_complete = transaction.OnComplete.NoOpOC.real

    params = client.suggested_params()

    args_list = [bytes(username, 'utf8'), bytes(usertype, 'utf8'), bytes(email, 'utf8'), bytes(password, 'utf8')]

    txn = transaction.ApplicationCreateTxn(sender, params, on_complete,
                                           approval_program, clear_program,
                                           global_schema, local_schema, args_list)
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    client.send_transactions([signed_txn])
    com_func.wait_for_confirmation(client, tx_id)
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['application-index']
    print("Created new admin user id: ", app_id)

    return string(app_id)


# update admin details on blockchain
def update_admin(client, admin_passphrase,admin_id, username, usertype, email, password):
    print("Updating existing admin....")

    approval_program = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)

    # Converting Passphrase to public and private key.
    private_key = mnemonic.to_private_key(admin_passphrase)
    public_address = account.address_from_private_key(private_key)

    # declare sender
    sender = public_address

    # get node suggested parameters
    params = client.suggested_params()

    app_args = [bytes(username, 'utf8'), bytes(usertype, 'utf8'), bytes(email, 'utf8'), bytes(password, 'utf8')]

    # create unsigned transaction
    txn = transaction.ApplicationUpdateTxn(sender, params, admin_id, approval_program, clear_program, app_args)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation

    confirmed_txn = com_func.wait_for_confirmation(client, tx_id)
    print("TXID: ", tx_id)
    print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))
    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['txn']['txn']['apid']

    return string(app_id)


# call admin app and create asset
def admin_asset(client, admin_passphrase, usertype, password, admin_id, total_nft, unit_name, asset_name, file_path):

    # define address from private key of creator
    creator_private_key = mnemonic.to_private_key(admin_passphrase)
    creator_account = account.address_from_private_key(creator_private_key)

    # set suggested params
    params = client.suggested_params()

    args = ["check_admin", bytes(usertype, 'utf-8'), bytes(password, 'utf-8')]

    print("Calling admin Application...")

    # admin to call app(admin): transaction 1
    sender = creator_account
    txn_1 = transaction.ApplicationNoOpTxn(sender, params, admin_id, args)
    print("Created Transaction 1: ", txn_1.get_txid())

    # creating asset: transaction 2
    txn_2 = transaction.AssetConfigTxn(sender=sender, sp=params, total=total_nft, default_frozen=False,
                                       unit_name=unit_name, asset_name=asset_name, manager=creator_account,
                                       reserve=creator_account, freeze=creator_account, clawback=creator_account,
                                       url=file_path, decimals=0)

    print("Created Transaction 2: ", txn_2.get_txid())

    # grouping both the txn to give the group id
    print("Grouping Transactions...")
    group_id = transaction.calculate_group_id([txn_1, txn_2])
    print("groupID of the Transaction: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id

    # split transaction group
    print("Splitting unsigned transaction group...")

    # signing the transactions
    stxn_1 = txn_1.sign(creator_private_key)
    print("Investor signed txn_1: ", stxn_1.get_txid())

    stxn_2 = txn_2.sign(creator_private_key)
    print("Investor signed txn_2: ", stxn_2.get_txid())
    txn_id_2 = stxn_2.get_txid()

    # grouping the sign transactions
    signedGroup = [stxn_1, stxn_2]

    # send transactions
    print("Sending transaction group...")
    tx_id = client.send_transactions(signedGroup)

    # wait for confirmation
    com_func.wait_for_confirmation(client, tx_id)

    ptx = client.pending_transaction_info(txn_id_2)
    asset_id = ptx["asset-index"]

    return string(asset_id)
