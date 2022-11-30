import json
from algosdk.future import transaction
from utilities.CommonFunctions import get_address_from_application, wait_for_confirmation
from algosdk import account, mnemonic, encoding
from Contracts import admin_contract, teal


# Declare application state storage (immutable)
local_ints = 0
local_bytes = 0
global_ints = 0
global_bytes = 1
global_schema = transaction.StateSchema(global_ints, global_bytes)
local_schema = transaction.StateSchema(local_ints, local_bytes)


# Generate a new admin account as well as new user id for each user that registers
def create_admin_account(client):
    print("Creating admin application...")

    # import smart contract for the application
    approval_program = teal.to_teal(admin_contract.approval_program())
    clear_program = teal.to_teal(admin_contract.clearstate_contract())

    mnemonic_keys = "loyal wrestle resemble true love access ship olive urban stick magnet verb bamboo anger open trip air heart laundry pulp dilemma divide ill abstract crack"
    private_key = mnemonic.to_private_key(mnemonic_keys)
    sender = account.address_from_private_key(private_key)

    on_complete = transaction.OnComplete.NoOpOC.real

    params = client.suggested_params()

    args_list = [bytes("admin", 'utf8')]

    txn = transaction.ApplicationCreateTxn(sender, params, on_complete,
                                           approval_program, clear_program,
                                           global_schema, local_schema, args_list)

    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    client.send_transactions([signed_txn])
    wait_for_confirmation(client, tx_id)
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['application-index']

    return app_id

#
# # update admin details on blockchain
# def update_admin(client, public_address, admin_id, name, usertype, email):
#     print("Updating existing admin....")
#
#     approval_program = com_func.compile_program(client, approval_program_source_initial)
#     clear_program = com_func.compile_program(client, clear_program_source)
#
#     # declare sender
#     sender = public_address
#
#     # get node suggested parameters
#     params = client.suggested_params()
#
#     app_args = [bytes(name, 'utf8'), bytes(usertype, 'utf8'), bytes(email, 'utf8')]
#
#     # create unsigned transaction
#     txn = transaction.ApplicationUpdateTxn(sender, params, admin_id, approval_program, clear_program, app_args)
#
#     txngrp = [{'txn':encoding.msgpack_encode (txn)}]
#
#     return txngrp


# call user app and create asset
def admin_asset(client, usertype, user_app_id, unit_name, asset_name, image_url, description):

    # define address from private key of creator
    creator_account = get_address_from_application(user_app_id)

    if usertype == 'creator' or usertype == 'admin':
        # set suggested params
        params = client.suggested_params()

        print("Minting NFT...")

        # note
        json_object = {
            'standard': 'arc69',
            'description': description,
            'external_url': image_url,
            'properties': {
                'from': 'www.cashdillo.com',
                'set': 'True',
                'type': 'Reward',
                'name': asset_name,
                'image': image_url
            }
        }
        note_field = json.dumps(json_object)

        # creating asset: transaction 2
        txn = transaction.AssetConfigTxn(sender=creator_account, sp=params, total=1, default_frozen=False,
                                         unit_name=unit_name, asset_name=asset_name, decimals=0, url=image_url,
                                         manager=creator_account, freeze="", reserve=creator_account,
                                         clawback="", strict_empty_address_check=False, note=note_field.encode())

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

    # Payment to admin application wallet to receive NFT
    txn_1 = transaction.PaymentTxn(
        sender=wallet_address,
        sp=params,
        receiver=marketplace_address,
        amt=int(0.3*1_000_000)
    )

    # Application call to optin NFT
    params_txn2 = client.suggested_params()
    params_txn2.fee = 2000
    txn_2 = transaction.ApplicationNoOpTxn(
        sender=wallet_address,
        sp=params_txn2,
        index=admin_app_id,
        foreign_assets=[asset_id],
        app_args=['Add NFT']
    )

    # Use the AssetTransferTxn class to transfer assets
    txn_3 = transaction.AssetTransferTxn(
        sender=wallet_address,
        sp=params,
        receiver=marketplace_address,
        amt=1,
        index=asset_id
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
def buy_nft(client, asset_id, user_app_id, nft_price, admin_app_id):

    # set suggested params
    params = client.suggested_params()

    # get the wallet address
    creator_address = get_address_from_application(user_app_id)
    # creator_address = wallet_address
    admin_wallet_address = get_address_from_application(admin_app_id)

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
    params_txn3 = client.suggested_params()
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
