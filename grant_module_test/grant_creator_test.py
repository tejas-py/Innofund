from algosdk import mnemonic
from algosdk.future.transaction import *
import transactions.index
from utilities.CommonFunctions import get_address_from_application, Today_seconds
from Contracts import grant_creator_contract, teal


# Create grant creator - Admin application
def grant_admin_app(client, mnemonic_keys, organisation_name, organisation_role, usertype):
    print('creating application...')

    # Declare application state storage (immutable)
    local_ints = 0
    local_bytes = 0
    global_ints = 0
    global_bytes = 3
    global_schema = StateSchema(global_ints, global_bytes)
    local_schema = StateSchema(local_ints, local_bytes)

    # derive private key and sender
    private_key = mnemonic.to_private_key(mnemonic_keys)
    sender = account.address_from_private_key(private_key)

    # import smart contract for the application
    approval_program = teal.to_teal(grant_creator_contract.admin())
    clear_program = teal.to_teal(grant_creator_contract.clearstate_contract())

    # define the params
    on_complete = OnComplete.NoOpOC.real
    params = client.suggested_params()
    args_list = [bytes(organisation_name, 'utf-8'), bytes(organisation_role, 'utf-8'), bytes(usertype, 'utf-8')]

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
    print("Created Grant Creator: ", app_id)

    return app_id


# create grant creator - manager application
def grant_manager_app(client, mnemonic_keys, grant_admin_app_id, usertype):

    # define the sender for the transaction
    print(f'Creating Manager by {grant_admin_app_id}...')
    sender = get_address_from_application(grant_admin_app_id)
    private_key = mnemonic.to_private_key(mnemonic_keys)

    # define params for transaction 1
    params = client.suggested_params()
    admin_app_address = encoding.encode_address(encoding.checksum(b'appID' + grant_admin_app_id.to_bytes(8, 'big')))

    # minimum balance is 300_000 for creating grant manager by the grant creator
    txn_1 = PaymentTxn(sender, params, admin_app_address, amt=300_000)

    # define params for transaction 2
    params_txn2 = client.suggested_params()
    params_txn2.fee = 2000
    params_txn2.flat_fee = True
    app_args = ['Create Manager', bytes(usertype, 'utf-8')]

    txn_2 = ApplicationNoOpTxn(sender, params_txn2, grant_admin_app_id, app_args, note="Creating manager for Cashdillo")

    # compute group id and put it into each transaction
    group_id = calculate_group_id([txn_1, txn_2])
    txn_1.group = group_id
    txn_2.group = group_id

    # sign transactions
    stxn_1 = txn_1.sign(private_key)
    stxn_2 = txn_2.sign(private_key)

    # assemble transaction group
    signedGroup = []
    signedGroup.append(stxn_1)
    signedGroup.append(stxn_2)

    # send transactions
    tx_id = client.send_transactions(signedGroup)

    # wait for confirmation

    wait_for_confirmation(client, tx_id, 4)

    # display results
    transaction_response = client.pending_transaction_info(stxn_2.get_txid())
    app_id = transaction_response['inner-txns'][0]['application-index']
    print("Created Grant Manager: ", app_id)

    return app_id


# creating grant by the grant creator and grant manager
def grant_app(client, mnemonic_keys, user_app_id, title, duration, min_grant, max_grant,
              total_grants, total_budget, grant_end_date, ESG):

    # define the sender for the transactions
    print(f'Creating Grant by {user_app_id}...')
    private_key = mnemonic.to_private_key(mnemonic_keys)
    sender = account.address_from_private_key(private_key)

    # define params for transaction 1
    params = client.suggested_params()
    admin_app_address = encoding.encode_address(encoding.checksum(b'appID' + user_app_id.to_bytes(8, 'big')))

    # minimum balance is 578_000 for creating grant by the grant creator + the grant the creator wants to give to the applicants
    txn_1 = PaymentTxn(sender, params, admin_app_address,
                       amt=578_000+int(total_budget*1_000_000)
                       )

    # define params for transaction 2
    params_txn2 = client.suggested_params()
    params_txn2.fee = 3000
    params_txn2.flat_fee = True
    app_args = ['Create Grant', bytes(title, 'utf-8'), int(duration),
                int(min_grant*1_000_000), int(max_grant*1_000_000), int(total_grants), int(total_budget*1_000_000), int(grant_end_date), int(ESG)]

    txn_2 = ApplicationNoOpTxn(sender, params_txn2, user_app_id, app_args, note="Creating Grant")

    # compute group id and put it into each transaction
    group_id = calculate_group_id([txn_1, txn_2])
    txn_1.group = group_id
    txn_2.group = group_id

    # sign transactions
    stxn_1 = txn_1.sign(private_key)
    stxn_2 = txn_2.sign(private_key)

    # assemble transaction group
    signedGroup = []
    signedGroup.append(stxn_1)
    signedGroup.append(stxn_2)

    # send transactions
    tx_id = client.send_transactions(signedGroup)

    # wait for confirmation
    wait_for_confirmation(client, tx_id, 4)

    # display results
    transaction_response = client.pending_transaction_info(stxn_2.get_txid())
    app_id = transaction_response['inner-txns'][0]['application-index']
    print("Created Grant by the Manager:", app_id)

    return app_id


# Edit Grand details
def edit_grant(client, mnemonic_keys, user_app_id, grant_app_id, title, duration, min_grant, max_grant,
               total_grants, total_budget, grant_end_date):

    # derive private key and sender
    private_key = mnemonic.to_private_key(mnemonic_keys)
    sender = get_address_from_application(user_app_id)

    # define the params
    params = client.suggested_params()
    params.fee = 1000
    args_list = ['Edit Grant', bytes(title, 'utf-8'), int(duration),
                 int(min_grant*1_000_000), int(max_grant*1_000_000), int(total_grants), int(total_budget*1_000_000), int(grant_end_date)]

    print('creating transaction object...')
    txn = ApplicationNoOpTxn(sender=sender, sp=params, index=grant_app_id, app_args=args_list)

    print("Signing Transaction...")
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    return tx_id


# Admin Approve/Reject the grant
def admin_grant_review(client, mnemonic_keys, review, grant_app_id):
    print('creating application...')
    # derive private key and sender
    private_key = mnemonic.to_private_key(mnemonic_keys)
    sender = account.address_from_private_key(private_key)

    # define the params
    params = client.suggested_params()
    params.fee = 1000
    args_list = ['Approve/Reject Grant by Admin', int(review)]

    print('creating transaction object...')
    txn = ApplicationNoOpTxn(sender=sender, sp=params, index=grant_app_id, app_args=args_list)

    print("Signing Transaction...")
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    return tx_id


# Approve the Applicant's Application for grant and transfer 10% of Advance money for Milestone 1
# user_app_id: Of the applicant to give advance money
def approve_grant_application(client, mnemonic_keys, wallet_address, application_app_id, user_app_id, grant_app_id):

    # derive the accounts
    private_key = mnemonic.to_private_key(mnemonic_keys)
    sender = wallet_address
    smart_contract_address = encoding.encode_address(encoding.checksum(b'appID' + application_app_id.to_bytes(8, 'big')))
    grant_applicant_wallet_address = get_address_from_application(user_app_id)

    # define the params
    params = client.suggested_params()
    params.fee = 4000
    params.flat_fee = True

    # define the ask amounts
    milestone_1_ask = int(str(transactions.index.app_param_value(application_app_id, "milestone_1")).split('/')[1])*1_000_000
    milestone_2_ask = int(str(transactions.index.app_param_value(application_app_id, "milestone_2")).split('/')[1])*1_000_000
    # 10% advance money to be credited right away after the approval of applicant's application
    advance_of_milestone_1 = milestone_1_ask * 10/100
    # total ask after the advance
    total_money = milestone_1_ask+milestone_2_ask-advance_of_milestone_1

    args_list = ["Approve grant application", "Change status to approve", int(total_money), int(advance_of_milestone_1), int(Today_seconds())]
    accounts_list = [smart_contract_address, grant_applicant_wallet_address]
    apps = [application_app_id]

    print('creating transaction object...')
    txn = ApplicationNoOpTxn(sender=sender, sp=params, index=grant_app_id, app_args=args_list, accounts=accounts_list, foreign_apps=apps)

    print("Signing Transaction...")
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    client.pending_transaction_info(tx_id)

    return tx_id


# approve milestone 1 by grant manager/creator
# user_app_id of the applicant
def milestone_1_approval(client, mnemonic_keys, wallet_address, application_app_id, user_app_id):

    # derive the accounts
    private_key = mnemonic.to_private_key(mnemonic_keys)
    sender = wallet_address
    grant_applicant_wallet_address = get_address_from_application(user_app_id)

    # define the params
    params = client.suggested_params()
    params.fee = 2000
    params.flat_fee = True

    # define the ask amounts
    milestone_1_ask = int(str(transactions.index.app_param_value(application_app_id, "milestone_1")).split('/')[1])*1_000_000
    milestone_2_ask = int(str(transactions.index.app_param_value(application_app_id, "milestone_2")).split('/')[1])*1_000_000
    # 10% advance money to be credited right away after the approval of applicant's application
    advance_of_milestone_1 = milestone_1_ask * 10/100
    advance_of_milestone_2 = milestone_2_ask * 10/100
    # total ask after the advance
    amount_to_give = milestone_1_ask - advance_of_milestone_1 + advance_of_milestone_2

    # check the deadline
    milestone_1_deadline = int(str(transactions.index.app_param_value(application_app_id, "milestone_1")).split('/')[0])

    if int(Today_seconds()) <= milestone_1_deadline:
        args_list = ["Approve Milestone 1", int(amount_to_give)]
        accounts_list = [grant_applicant_wallet_address]

        print('creating transaction object...')
        txn = ApplicationNoOpTxn(sender=sender, sp=params, index=application_app_id, app_args=args_list, accounts=accounts_list, note="Grant Milestone 1 Approved")

        print("Signing Transaction...")
        signed_txn = txn.sign(private_key)
        tx_id = signed_txn.transaction.get_txid()

        # send transaction
        client.send_transactions([signed_txn])

        # await confirmation
        wait_for_confirmation(client, tx_id)

        # display results
        client.pending_transaction_info(tx_id)

        return tx_id
    else:
        return ({'message': "Milestone 1 Deadline Reached"})


# approve milestone 2 by grant manager/creator
# user_app_id of the applicant
def milestone_2_approval(client, mnemonic_keys, wallet_address, application_app_id, user_app_id):

    # derive the accounts
    private_key = mnemonic.to_private_key(mnemonic_keys)
    sender = wallet_address
    grant_applicant_wallet_address = get_address_from_application(user_app_id)

    # define the params
    params = client.suggested_params()
    params.fee = 2000
    params.flat_fee = True

    # define the ask amounts
    milestone_2_ask = int(str(transactions.index.app_param_value(application_app_id, "milestone_2")).split('/')[1])*1_000_000
    # 10% advance money to be credited right away after the approval of applicant's application
    advance_of_milestone_2 = milestone_2_ask * 10/100
    # total ask after the advance
    amount_to_give = milestone_2_ask - advance_of_milestone_2

    # check the deadline
    milestone_2_deadline = int(str(transactions.index.app_param_value(application_app_id, "milestone_2")).split('/')[0])

    if int(Today_seconds()) <= milestone_2_deadline:
        args_list = ["Approve Milestone 2", int(0), int(amount_to_give)]
        accounts_list = [grant_applicant_wallet_address]

        print('creating transaction object...')
        txn = ApplicationNoOpTxn(sender=sender, sp=params, index=application_app_id, app_args=args_list, accounts=accounts_list)

        print("Signing Transaction...")
        signed_txn = txn.sign(private_key)
        tx_id = signed_txn.transaction.get_txid()

        # send transaction
        client.send_transactions([signed_txn])

        # await confirmation
        wait_for_confirmation(client, tx_id)

        # display results
        client.pending_transaction_info(tx_id)

        return tx_id
    else:
        return ({'message': "Milestone 1 Deadline Reached"})


# Milestone Rejected by Grant Creator/Manager
# user_app_id of the grant creator
def milestone_rejected(client, mnemonic_keys, wallet_address, application_app_id, user_app_id):

    # derive the accounts
    private_key = mnemonic.to_private_key(mnemonic_keys)
    sender = wallet_address
    smart_contract_address = encoding.encode_address(encoding.checksum(b'appID' + application_app_id.to_bytes(8, 'big')))
    grant_wallet_address = get_address_from_application(user_app_id)

    # define the params
    params = client.suggested_params()
    params.fee = 2000
    params.flat_fee = True

    # define the amount to be given
    account_information = client.account_info(smart_contract_address)
    amount_to_return = account_information['amount']

    args_list = ["Reject Milestone", int(amount_to_return)]
    accounts_list = [grant_wallet_address]

    print('creating transaction object...')
    txn = ApplicationNoOpTxn(sender=sender, sp=params, index=application_app_id, app_args=args_list, accounts=accounts_list, note="Grant Milestone Rejected")

    print("Signing Transaction...")
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    client.pending_transaction_info(tx_id)

    return tx_id


# find the balance
def balance(client, app_id):
    wallet_address = encoding.encode_address(encoding.checksum(b'appID' + app_id.to_bytes(8, 'big')))
    account_i = client.account_info(wallet_address)
    locked_balance = account_i['min-balance']
    account_balance = account_i['amount']
    print(f"min: {locked_balance}")
    print(f"max: {account_balance}")
