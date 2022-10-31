from algosdk import mnemonic
from algosdk.future.transaction import *
from utilities.CommonFunctions import Today_seconds, get_address_from_application
from Contracts import grant_applicant_contract, teal


# create account for grant applicant
def grant_applicant_app(client, wallet_address, usertype):
    print('creating application...')

    # Declare application state storage (immutable)
    local_ints = 0
    local_bytes = 0
    global_ints = 0
    global_bytes = 1
    global_schema = StateSchema(global_ints, global_bytes)
    local_schema = StateSchema(local_ints, local_bytes)

    # derive private key and sender
    sender = wallet_address

    # import smart contract for the application
    approval_program = teal.to_teal(grant_applicant_contract.grant_applicant())
    clear_program = teal.to_teal(grant_applicant_contract.clearstate_contract())

    # define the params
    on_complete = OnComplete.NoOpOC.real
    params = client.suggested_params()
    args_list = [bytes(usertype, 'utf-8')]

    print('creating transaction object...')
    txn = ApplicationCreateTxn(sender=sender, sp=params, on_complete=on_complete,
                               approval_program=approval_program, clear_program=clear_program,
                               global_schema=global_schema, local_schema=local_schema, app_args=args_list)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# submit the application for the grant (creating an application)
def application_app(client, wallet_address, user_app_id, mile1, mile2, req_funds, grant_app_id):

    # define the sender for the transaction
    print(f'Creating Application by {user_app_id}...')
    sender = wallet_address
    # define params for transaction 1
    params = client.suggested_params()
    admin_app_address = encoding.encode_address(encoding.checksum(b'appID' + user_app_id.to_bytes(8, 'big')))

    # minimum balance is 407_000 for creating application by the applicant
    txn_1 = PaymentTxn(sender, params, admin_app_address, amt=407_000)

    # define params for transaction 2
    params_txn2 = client.suggested_params()
    params_txn2.fee = 2000
    params_txn2.flat_fee = True
    app_args = ['Create Grant Application', int(grant_app_id), bytes(mile1, 'utf-8'), bytes(mile2, 'utf-8'), int(req_funds*1_000_000)]

    txn_2 = ApplicationNoOpTxn(sender, params_txn2, user_app_id, app_args, note="Creating Grant Application.")

    # define params for transaction 3
    params_txn3 = client.suggested_params()
    milestone_1_end_date = mile1.split('/')[0]
    milestone_2_end_date = mile2.split('/')[0]
    app_args_txn3 = ['Apply for grant', int(Today_seconds()), int(req_funds*1_000_000), int(milestone_1_end_date), int(milestone_2_end_date)]
    txn_3 = ApplicationNoOpTxn(sender, params_txn3, grant_app_id, app_args_txn3, note="Applying for Grant")

    print("Grouping transactions...")
    # compute group id and put it into each transaction
    group_id = calculate_group_id([txn_1, txn_2, txn_3])
    print("...computed groupId: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id
    txn_3.group = group_id

    txngrp = [{'txn': encoding.msgpack_encode(txn_1)},
              {'txn': encoding.msgpack_encode(txn_2)},
              {'txn': encoding.msgpack_encode(txn_3)}]

    return txngrp


# Edit the Application form
def edit_application_form(client, application_app_id, user_app_id, mile1, mile2, req_funds):

    # derive private key and sender
    sender = get_address_from_application(user_app_id)

    # define the params
    params = client.suggested_params()
    params.fee = 1000
    args_list = ['Edit Grant', bytes(mile1, 'utf-8'), bytes(mile2, 'utf-8'), int(req_funds*1_000_000)]

    print('creating transaction object...')
    txn = ApplicationNoOpTxn(sender=sender, sp=params, index=application_app_id, app_args=args_list)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp
