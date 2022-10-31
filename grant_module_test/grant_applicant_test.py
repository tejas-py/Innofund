from algosdk import mnemonic
from algosdk.future.transaction import *
from utilities.CommonFunctions import Today_seconds, get_address_from_application
from Contracts import grant_applicant_contract, teal


# create account for grant applicant
def grant_applicant_app(client, mnemonic_keys, usertype):
    print('creating application...')

    # Declare application state storage (immutable)
    local_ints = 0
    local_bytes = 0
    global_ints = 0
    global_bytes = 1
    global_schema = StateSchema(global_ints, global_bytes)
    local_schema = StateSchema(local_ints, local_bytes)

    # derive private key and sender
    private_key = mnemonic.to_private_key(mnemonic_keys)
    sender = account.address_from_private_key(private_key)

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

    print("Signing Transaction...")
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['application-index']
    print("Created Grant Applicant: ", app_id)

    return app_id


# submit the application for the grant (creating an application)
def application_app(client, wallet_address, mnemonic_keys, user_app_id, mile1, mile2, req_funds, grant_app_id):

    # define the sender for the transaction
    print(f'Creating Application by {user_app_id}...')
    sender = wallet_address
    private_key = mnemonic.to_private_key(mnemonic_keys)
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

    # compute group id and put it into each transaction
    group_id = calculate_group_id([txn_1, txn_2, txn_3])
    txn_1.group = group_id
    txn_2.group = group_id
    txn_3.group = group_id

    # sign transactions
    stxn_1 = txn_1.sign(private_key)
    stxn_2 = txn_2.sign(private_key)
    stxn_3 = txn_3.sign(private_key)

    # assemble transaction group
    signedGroup = []
    signedGroup.append(stxn_1)
    signedGroup.append(stxn_2)
    signedGroup.append(stxn_3)

    # send transactions
    tx_id = client.send_transactions(signedGroup)

    # wait for confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(stxn_2.get_txid())
    app_id = transaction_response['inner-txns'][0]['application-index']
    print("Created Application: ", app_id)

    return app_id


# Edit the Application form
def edit_application_form(client, mnemonic_keys, application_app_id, user_app_id, mile1, mile2, req_funds):

    # derive private key and sender
    private_key = mnemonic.to_private_key(mnemonic_keys)
    sender = get_address_from_application(user_app_id)

    # define the params
    params = client.suggested_params()
    params.fee = 1000
    args_list = ['Edit Grant', bytes(mile1, 'utf-8'), bytes(mile2, 'utf-8'), int(req_funds*1_000_000)]

    print('creating transaction object...')
    txn = ApplicationNoOpTxn(sender=sender, sp=params, index=application_app_id, app_args=args_list)

    print("Signing Transaction...")
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    return tx_id


# find the balance
def balance(client, app_id):
    wallet_address = encoding.encode_address(encoding.checksum(b'appID' + app_id.to_bytes(8, 'big')))
    account_i = client.account_info(wallet_address)
    locked_balance = account_i['min-balance']
    account_balance = account_i['amount']
    print(f"min: {locked_balance}")
    print(f"max: {account_balance}")
