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
approval_program_source_initial = b"""#pragma version 6
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
txna ApplicationArgs 0
byte "Withdraw NFT"
==
bnz main_l9
global GroupSize
int 3
==
txna ApplicationArgs 0
byte "Buy NFT"
==
&&
bnz main_l8
err
main_l8:
itxn_begin
int axfer
itxn_field TypeEnum
txna Accounts 1
itxn_field AssetReceiver
int 10
itxn_field AssetAmount
txna Assets 0
itxn_field XferAsset
int 0
itxn_field Fee
byte "NFT bought from Cashdillo Market-Place"
itxn_field Note
itxn_submit
int 1
return
main_l9:
itxn_begin
int axfer
itxn_field TypeEnum
txna Accounts 0
itxn_field AssetReceiver
int 10
itxn_field AssetAmount
txna Assets 0
itxn_field XferAsset
int 0
itxn_field Fee
byte "NFT withdraw from Cashdillo Market-Place"
itxn_field Note
itxn_submit
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
def admin_asset(client, usertype, user_app_id, unit_name, asset_name, image_url, amt):

    # define address from private key of creator
    creator_account = com_func.get_address_from_application(user_app_id)

    if usertype == 'creator' or usertype == 'admin':
        # set suggested params
        params = client.suggested_params()
        params.fee = amt
        params.flat_fee = True

        print("Minting NFT...")

        # creating asset: transaction 2
        txn = transaction.AssetConfigTxn(sender=creator_account, sp=params, total=10, default_frozen=False,
                                         unit_name=unit_name, asset_name=asset_name, decimals=1, url=image_url,
                                         manager=creator_account, freeze=creator_account, reserve=creator_account,
                                         clawback=creator_account)

        result = [{'txn': encoding.msgpack_encode(txn)}]

    else:
        result = {'message': 'only creators and admin can mint the nft'}

    return result


# transfer nft to admin application for marketplace
def transfer_nft_to_application(client, asset_id, admin_app_id, wallet_address):

    # get the wallet address of the admin application
    marketplace_address = encoding.encode_address(encoding.checksum(b'appID' + admin_app_id.to_bytes(8, 'big')))

    print(f"Opt-in {asset_id} Asset...")
    # set suggested params
    params = client.suggested_params()

    # Use the AssetTransferTxn opt-in
    txn_1 = transaction.AssetTransferTxn(
        sender=wallet_address,
        sp=params,
        receiver=marketplace_address,
        amt=0,
        index=asset_id)

    # Use the AssetTransferTxn class to transfer assets
    txn_2 = transaction.AssetTransferTxn(
        sender=wallet_address,
        sp=params,
        receiver=marketplace_address,
        amt=10,
        index=asset_id)

    print("Grouping transactions...")
    # compute group id and put it into each transaction
    group_id = transaction.calculate_group_id([txn_1, txn_2])
    print("...computed groupId: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id

    txngrp = [{'txn': encoding.msgpack_encode(txn_1)},
              {'txn': encoding.msgpack_encode(txn_2)}]

    return txngrp


# withdraw nft from the marketplace
def withdraw_nft_from_marketplace(client, asset_id, admin_app_id, wallet_address):

    # set suggested params
    params = client.suggested_params()
    params.fee = 2000
    params.flat_fee = True

    # application call to transfer nft from admin app to admin wallet address
    args = ['Withdraw NFT']
    asset_list = [asset_id]
    txn = transaction.ApplicationNoOpTxn(wallet_address, params, admin_app_id, args, foreign_assets=asset_list)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# buy nft from admin
def buy_nft(client, asset_id, user_app_id, nft_price):

    # set suggested params
    params = client.suggested_params()

    # get the wallet address
    admin_app_id = 107294801
    creator_address = com_func.get_address_from_application(user_app_id)
    admin_wallet_address = com_func.get_address_from_application(admin_app_id)

    # Optin NFT
    txn_1 = transaction.AssetTransferTxn(
        sender=creator_address,
        sp=params,
        receiver=creator_address,
        amt=0,
        index=asset_id)

    # Payment to admin for NFT
    txn_2 = transaction.PaymentTxn(
        sender=creator_address,
        sp=params,
        receiver=admin_wallet_address,
        amt=nft_price,
        note=f"Payment of NFT from {creator_address} for NFT: {asset_id}"
    )

    # Application call to receive nft
    # parameters
    params_txn3 = client.suggested_params
    params_txn3.fee = 2000
    params_txn3.flat_fee = True

    # arguments
    args = ['Buy NFT']
    asset_list = [asset_id]
    account_list = [creator_address]

    txn_3 = transaction.ApplicationNoOpTxn(
        sender=creator_address,
        index=admin_app_id,
        sp=params_txn3,
        app_args=args,
        foreign_assets=asset_list,
        accounts=account_list,
        note='NFT bought from Cashdillo Market-Place'
    )

    print("Grouping transactions...")
    # compute group id and put it into each transaction
    group_id = transaction.calculate_group_id([txn_1, txn_2, txn_3])
    print("...computed groupId: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id
    txn_3.group = group_id

    txngrp = [{'txn': encoding.msgpack_encode(txn_1)},
              {'txn': encoding.msgpack_encode(txn_2)},
              {'txn': encoding.msgpack_encode(txn_3)}]

    return txngrp

