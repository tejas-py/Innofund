from algosdk.future.transaction import *

import API.connection
import transactions.index
from utilities.CommonFunctions import get_address_from_application, Today_seconds, compile_program

# Smart Contract of the Grant Creator
approval_program_source = b"""#pragma version 6
txn ApplicationID
int 0
==
bnz main_l16
txn OnCompletion
int NoOp
==
bnz main_l7
txn OnCompletion
int DeleteApplication
==
bnz main_l4
err
main_l4:
txn Sender
global CreatorAddress
==
bnz main_l6
err
main_l6:
int 1
return
main_l7:
txna ApplicationArgs 0
byte "Create Manager"
==
bnz main_l15
txna ApplicationArgs 0
byte "Create Grant"
==
bnz main_l14
txn Sender
global CreatorAddress
==
txna ApplicationArgs 0
byte "Delete Grant"
==
&&
bnz main_l13
txna ApplicationArgs 0
byte "Delete Manager"
==
bnz main_l12
err
main_l12:
itxn_begin
int appl
itxn_field TypeEnum
txna Applications 1
itxn_field ApplicationID
int DeleteApplication
itxn_field OnCompletion
int 0
itxn_field Fee
itxn_next
int pay
itxn_field TypeEnum
int 300000
itxn_field Amount
global CreatorAddress
itxn_field Receiver
int 0
itxn_field Fee
itxn_submit
int 1
return
main_l13:
itxn_begin
int appl
itxn_field TypeEnum
txna Applications 1
itxn_field ApplicationID
int DeleteApplication
itxn_field OnCompletion
global CreatorAddress
itxn_field Accounts
int 0
itxn_field Fee
itxn_next
int pay
itxn_field TypeEnum
int 578000
itxn_field Amount
global CreatorAddress
itxn_field Receiver
int 0
itxn_field Fee
itxn_submit
int 1
return
main_l14:
global GroupSize
int 2
==
assert
gtxn 0 TypeEnum
int pay
==
assert
gtxn 1 TypeEnum
int appl
==
assert
global CurrentApplicationAddress
acct_params_get AcctBalance
store 3
store 2
load 2
assert
itxn_begin
int appl
itxn_field TypeEnum
int 3
itxn_field GlobalNumByteSlice
int 9
itxn_field GlobalNumUint
byte 0x062003010006260e067374617475731b61636365707465645f6772616e745f6170706c69636174696f6e7308617070726f7665640b676976656e5f6772616e740c746f74616c5f6772616e74730e6772616e745f656e645f646174650763726561746f720770656e64696e670c746f74616c5f627564676574096d696e5f6772616e74096d61785f6772616e74057469746c65086475726174696f6e184368616e67652073746174757320746f20617070726f76653118231240029831192312400036311981051240000100320a73003501350031003209124428642a1344320481021244b122b210361c01b20923b201b3340023124422433204810312361a00800f4170706c7920666f72206772616e7412104001f2310027066412361a008019417070726f7665206772616e74206170706c69636174696f6e1210400172310027066412361a00801e417070726f7665206c617374206772616e74206170706c69636174696f6e12104000f3361a00801852656a656374206772616e74206170706c69636174696f6e124000a1310027066412361a00800a45646974204772616e74121040004f361a00801d417070726f76652f52656a656374204772616e742062792041646d696e1240000100361a0117221240001428642707124428800872656a6563746564672243286427071244282a672243286427071244270b361a0167270c361a0217672709361a031767270a361a0417672704361a0517672708361a0617672705361a071767224328642a1244b124b210363201b21880194368616e67652073746174757320746f2072656a6563746564b21a23b201b3224328642a124427046429640d44b124b210363201b218270db21a23b201b622b210361c02b207361a0317b20823b201b622b210361c01b20923b201b32929642208672b2b64361a021708361a03170867224328642a124427046429640d44b124b210363201b218270db21a23b201b622b210361c01b207361a0217b20823b201b622b210361c02b207361a0317b20823b201b32929642208672b2b64361a021708361a03170867224328642a124427046429640d44361a01172705640c44361a03172705640d44361a04172705640d442708642b640d44361a02172708640e44361a02172709640f44361a0217270a640e442243311b81091244270b361a0067270c361a0117672709361a021767270a361a0317672704361a0417672708361a0517672705361a0617678003455347361a0717672b2367282707672706361a08672923672243
itxn_field ApprovalProgram
byte 0x06810143
itxn_field ClearStateProgram
txna ApplicationArgs 1
itxn_field ApplicationArgs
txna ApplicationArgs 2
itxn_field ApplicationArgs
txna ApplicationArgs 3
itxn_field ApplicationArgs
txna ApplicationArgs 4
itxn_field ApplicationArgs
txna ApplicationArgs 5
itxn_field ApplicationArgs
txna ApplicationArgs 6
itxn_field ApplicationArgs
txna ApplicationArgs 7
itxn_field ApplicationArgs
txna ApplicationArgs 8
itxn_field ApplicationArgs
global CreatorAddress
itxn_field ApplicationArgs
int NoOp
itxn_field OnCompletion
int 0
itxn_field Fee
itxn_submit
itxn CreatedApplicationID
app_params_get AppAddress
store 1
store 0
itxn_begin
int pay
itxn_field TypeEnum
load 0
itxn_field Receiver
txna ApplicationArgs 6
btoi
itxn_field Amount
int 0
itxn_field Fee
itxn_submit
int 1
return
main_l15:
txn Sender
global CreatorAddress
==
assert
global GroupSize
int 2
==
assert
gtxn 0 TypeEnum
int pay
==
assert
gtxn 1 TypeEnum
int appl
==
assert
itxn_begin
int appl
itxn_field TypeEnum
int 2
itxn_field GlobalNumByteSlice
int 0
itxn_field GlobalNumUint
byte 0x0620050001060502311822124004933119221240001331192512400001003100320912400001002343361a00800c437265617465204772616e7412400039361a00800c44656c657465204772616e741240000100b124b210363201b21825b21922b201b623b21081d0a323b2083209b20722b201b32343320421041244330010231244330110241244320a730035033502340244b124b2108103b2358109b23480a607062003010006260e067374617475731b61636365707465645f6772616e745f6170706c69636174696f6e7308617070726f7665640b676976656e5f6772616e740c746f74616c5f6772616e74730e6772616e745f656e645f646174650763726561746f720770656e64696e670c746f74616c5f627564676574096d696e5f6772616e74096d61785f6772616e74057469746c65086475726174696f6e184368616e67652073746174757320746f20617070726f76653118231240029831192312400036311981051240000100320a73003501350031003209124428642a1344320481021244b122b210361c01b20923b201b3340023124422433204810312361a00800f4170706c7920666f72206772616e7412104001f2310027066412361a008019417070726f7665206772616e74206170706c69636174696f6e1210400172310027066412361a00801e417070726f7665206c617374206772616e74206170706c69636174696f6e12104000f3361a00801852656a656374206772616e74206170706c69636174696f6e124000a1310027066412361a00800a45646974204772616e74121040004f361a00801d417070726f76652f52656a656374204772616e742062792041646d696e1240000100361a0117221240001428642707124428800872656a6563746564672243286427071244282a672243286427071244270b361a0167270c361a0217672709361a031767270a361a0417672704361a0517672708361a0617672705361a071767224328642a1244b124b210363201b21880194368616e67652073746174757320746f2072656a6563746564b21a23b201b3224328642a124427046429640d44b124b210363201b218270db21a23b201b622b210361c02b207361a0317b20823b201b622b210361c01b20923b201b32929642208672b2b64361a021708361a03170867224328642a124427046429640d44b124b210363201b218270db21a23b201b622b210361c01b207361a0217b20823b201b622b210361c02b207361a0317b20823b201b32929642208672b2b64361a021708361a03170867224328642a124427046429640d44361a01172705640c44361a03172705640d44361a04172705640d442708642b640d44361a02172708640e44361a02172709640f44361a0217270a640e442243311b81091244270b361a0067270c361a0117672709361a021767270a361a0317672704361a0417672708361a0517672705361a0617678003455347361a0717672b2367282707672706361a08672923672243b21e800406810143b21f361a01b21a361a02b21a361a03b21a361a04b21a361a05b21a361a06b21a361a07b21a361a08b21a3100b21a22b21922b201b3b43d720835013500b123b2103400b207361a0617b20822b201b32343311b2104124480116f7267616e69736174696f6e5f6e616d65361a006780087573657274797065361a01672343
itxn_field ApprovalProgram
byte 0x06810143
itxn_field ClearStateProgram
byte "organisation_name"
app_global_get
itxn_field ApplicationArgs
txna ApplicationArgs 1
itxn_field ApplicationArgs
int NoOp
itxn_field OnCompletion
int 0
itxn_field Fee
itxn_submit
int 1
return
main_l16:
txn NumAppArgs
int 3
==
assert
byte "organisation_name"
txna ApplicationArgs 0
app_global_put
byte "organisation_role"
txna ApplicationArgs 1
app_global_put
byte "usertype"
txna ApplicationArgs 2
app_global_put
int 1
return  
"""


# declare clear state program source
clear_program_source = b"""#pragma version 6
int 1
"""


# Create grant creator - Admin application
def grant_admin_app(client, wallet_address, organisation_name, organisation_role, usertype):
    print('creating application...')

    # Declare application state storage (immutable)
    local_ints = 0
    local_bytes = 0
    global_ints = 0
    global_bytes = 3
    global_schema = StateSchema(global_ints, global_bytes)
    local_schema = StateSchema(local_ints, local_bytes)

    # derive private key and sender
    sender = wallet_address

    # import smart contract for the application
    approval_program = compile_program(client, approval_program_source)
    clear_program = compile_program(client, clear_program_source)

    # define the params
    on_complete = OnComplete.NoOpOC.real
    params = client.suggested_params()
    args_list = [bytes(organisation_name, 'utf-8'), bytes(organisation_role, 'utf-8'), bytes(usertype, 'utf-8')]

    print('creating transaction object...')
    txn = ApplicationCreateTxn(sender=sender, sp=params, on_complete=on_complete,
                               approval_program=approval_program, clear_program=clear_program,
                               global_schema=global_schema, local_schema=local_schema, app_args=args_list, extra_pages=2)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# create grant creator - manager application
def grant_manager_app(client, grant_admin_app_id, usertype):

    # define the sender for the transaction
    print(f'Creating Manager by {grant_admin_app_id}...')
    sender = get_address_from_application(grant_admin_app_id)

    # define params for transaction 1
    params = client.suggested_params()
    admin_app_address = encoding.encode_address(encoding.checksum(b'appID' + grant_admin_app_id.to_bytes(8, 'big')))

    if transactions.index.balance(client, grant_admin_app_id)['max'] == 0:
        # minimum balance is 400_000 for creating grant manager by the grant creator for the first time
        txn_1 = PaymentTxn(sender, params, admin_app_address, amt=400_000)

    else:
        # minimum balance is 400_000 for creating grant manager by the grant creator
        txn_1 = PaymentTxn(sender, params, admin_app_address, amt=300_000)

    # define params for transaction 2
    params_txn2 = client.suggested_params()
    params_txn2.fee = 2000
    params_txn2.flat_fee = True
    app_args = ['Create Manager', bytes(usertype, 'utf-8')]

    txn_2 = ApplicationNoOpTxn(sender, params_txn2, grant_admin_app_id, app_args, note="Creating manager for Cashdillo")

    print("Grouping transactions...")
    # compute group id and put it into each transaction
    group_id = calculate_group_id([txn_1, txn_2])
    print("...computed groupId: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id

    txngrp = [{'txn': encoding.msgpack_encode(txn_1)},
              {'txn': encoding.msgpack_encode(txn_2)}]

    return txngrp


# delete Manager
def delete_manager(client, creator_app_id, manager_app_id):

    # derive private key and sender
    sender = get_address_from_application(creator_app_id)

    # define the params
    params = client.suggested_params()
    params.fee = 3000
    args_list = ['Delete Manager']
    app_list = [manager_app_id]

    print('creating transaction object...')
    txn = ApplicationNoOpTxn(sender=sender, sp=params, index=creator_app_id, app_args=args_list, foreign_apps=app_list)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# creating grant by the grant creator and grant manager
def grant_app(client, user_app_id, title, duration, min_grant, max_grant,
              total_grants, total_budget, grant_end_date, ESG, wallet_address):

    # define the sender for the transactions
    print(f'Creating Grant by {user_app_id}...')
    sender = wallet_address

    # define params for transaction 1
    params = client.suggested_params()
    admin_app_address = encoding.encode_address(encoding.checksum(b'appID' + user_app_id.to_bytes(8, 'big')))

    if transactions.index.grant_number_by_grant_creator(user_app_id) == 0:
        # minimum balance is 578_000 for creating grant by the grant creator + the grant the creator wants to give to the applicants
        txn_1 = PaymentTxn(sender, params, admin_app_address,
                           amt=678_000+int(total_budget*1_000_000)
                           )
    else:
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

    print("Grouping transactions...")
    # compute group id and put it into each transaction
    group_id = calculate_group_id([txn_1, txn_2])
    print("...computed groupId: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id

    txngrp = [{'txn': encoding.msgpack_encode(txn_1)},
              {'txn': encoding.msgpack_encode(txn_2)}]

    return txngrp


# Edit Grand details
def edit_grant(client, user_app_id, grant_app_id, title, duration, min_grant, max_grant,
               total_grants, total_budget, grant_end_date):

    # derive private key and sender
    sender = get_address_from_application(user_app_id)

    # define the params
    params = client.suggested_params()
    params.fee = 1000
    args_list = ['Edit Grant', bytes(title, 'utf-8'), int(duration),
                 int(min_grant*1_000_000), int(max_grant*1_000_000), int(total_grants), int(total_budget*1_000_000), int(grant_end_date)]

    print('creating transaction object...')
    txn = ApplicationNoOpTxn(sender=sender, sp=params, index=grant_app_id, app_args=args_list)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# Delete Grant
def delete_grant(client, user_app_id, grant_app_id):

    # get the sender
    sender = get_address_from_application(user_app_id)

    # define the params
    params = client.suggested_params()
    params.fee = 4000
    args_list = ['Delete Grant']
    app_list = [grant_app_id]

    print('creating transaction object...')
    txn = ApplicationNoOpTxn(sender=sender, sp=params, index=user_app_id, app_args=args_list, foreign_apps=app_list)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# Admin Approve/Reject the grant
def admin_grant_review(client, wallet_address, review, grant_app_id):
    print('creating application...')
    # derive private key and sender
    sender = wallet_address

    # define the params
    params = client.suggested_params()
    params.fee = 1000
    args_list = ['Approve/Reject Grant by Admin', int(review)]

    print('creating transaction object...')
    txn = ApplicationNoOpTxn(sender=sender, sp=params, index=grant_app_id, app_args=args_list)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# Approve the Applicant's Application for grant and transfer 10% of Advance money for Milestone 1
# user_app_id: Of the applicant to give advance money
def approve_grant_application(client, wallet_address, application_app_id, grant_app_id):

    # derive the accounts
    sender = wallet_address
    smart_contract_address = encoding.encode_address(encoding.checksum(b'appID' + application_app_id.to_bytes(8, 'big')))

    # get the wallet address of the applicant
    applicant_smart_contract_address = get_address_from_application(application_app_id)
    indexer_client = API.connection.connect_indexer()
    res = indexer_client.search_transactions(address=applicant_smart_contract_address)
    applicant_wallet_address = res['transactions'][0]['sender']

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
    # given grant and total budget of the grant
    total_budget = int(transactions.index.app_param_value(grant_app_id, 'total_budget'))
    given_grant = int(transactions.index.app_param_value(grant_app_id, 'given_grant'))
    # Grant amount left in smart contract
    budget_left_in_smart_contract = total_budget - given_grant

    # check if the application is the last application to approve for the grant
    total_ask_amount = (milestone_1_ask + milestone_2_ask)
    if (budget_left_in_smart_contract - total_ask_amount) > 100_000:
        # Transactions for all the grant application to approve
        args_list = ["Approve grant application", "Change status to approve", int(total_money), int(advance_of_milestone_1)]
        accounts_list = [smart_contract_address, applicant_wallet_address]
        apps = [application_app_id]
        print('creating transaction object...')
        txn = ApplicationNoOpTxn(sender=sender, sp=params, index=grant_app_id, app_args=args_list, accounts=accounts_list, foreign_apps=apps)

    else:
        # transaction for the last grant application to approve
        args_list = ["Approve last grant application", "Change status to approve", int(total_money), int(advance_of_milestone_1)]
        accounts_list = [smart_contract_address, applicant_wallet_address]
        apps = [application_app_id]

        print('creating transaction object...')
        txn = ApplicationNoOpTxn(sender=sender, sp=params, index=grant_app_id, app_args=args_list, accounts=accounts_list, foreign_apps=apps)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# Reject grant application
def reject_grant_application(client, wallet_address, application_app_id, grant_app_id):
    # derive the accounts
    sender = wallet_address

    # define the params
    params = client.suggested_params()
    params.fee = 2000
    params.flat_fee = True

    args_list = ["Reject grant application"]
    apps = [application_app_id]

    print('creating transaction object...')
    txn = ApplicationNoOpTxn(sender=sender, sp=params, index=grant_app_id, app_args=args_list, foreign_apps=apps)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# approve milestone 1 by grant manager/creator
def milestone_1_approval(client, wallet_address, application_app_id):

    # derive the accounts
    sender = wallet_address
    applicant_smart_contract_address = get_address_from_application(application_app_id)

    # get the wallet address of the applicant
    indexer_client = API.connection.connect_indexer()
    res = indexer_client.search_transactions(address=applicant_smart_contract_address)

    applicant_wallet_address = res['transactions'][0]['sender']

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
        accounts_list = [applicant_wallet_address]

        print('creating transaction object...')
        txn = ApplicationNoOpTxn(sender=sender, sp=params, index=application_app_id, app_args=args_list, accounts=accounts_list, note="Grant Milestone 1 Approved")

        txngrp = [{'txn': encoding.msgpack_encode(txn)}]

        return txngrp
    else:
        return ({'message': "Milestone 1 Deadline Reached"})


# approve milestone 2 by grant manager/creator
def milestone_2_approval(client, wallet_address, application_app_id):

    # derive the accounts
    sender = wallet_address
    applicant_smart_contract_address = get_address_from_application(application_app_id)

    # get the wallet address of the applicant
    indexer_client = API.connection.connect_indexer()
    res = indexer_client.search_transactions(address=applicant_smart_contract_address)
    applicant_wallet_address = res['transactions'][0]['sender']

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
        accounts_list = [applicant_wallet_address]

        print('creating transaction object...')
        txn = ApplicationNoOpTxn(sender=sender, sp=params, index=application_app_id, app_args=args_list, accounts=accounts_list)

        txngrp = [{'txn': encoding.msgpack_encode(txn)}]

        return txngrp
    else:
        return ({'message': "Milestone 2 Deadline Reached"})


# Milestone Rejected by Grant Creator/Manager
# user_app_id of the grant creator
def milestone_rejected(client, wallet_address, application_app_id, user_app_id):

    # derive the accounts
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

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp
