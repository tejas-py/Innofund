from algosdk.future.transaction import *
import transactions.index
from utilities.CommonFunctions import get_address_from_application, Today_seconds, compile_program

# Smart Contract of the Grant Creator
approval_program_source = b"""#pragma version 6
txn ApplicationID
int 0
==
bnz main_l14
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
bnz main_l13
txna ApplicationArgs 0
byte "Create Grant"
==
bnz main_l12
txna ApplicationArgs 0
byte "Delete Grant"
==
bnz main_l11
err
main_l11:
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
int 578000
itxn_field Amount
global CreatorAddress
itxn_field Receiver
int 0
itxn_field Fee
itxn_submit
int 1
return
main_l12:
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
int 8
itxn_field GlobalNumUint
byte 0x062003010006260d067374617475730e6772616e745f656e645f646174650770656e64696e670763726561746f7208617070726f7665640c746f74616c5f6275646765740b676976656e5f6772616e74096d696e5f6772616e74096d61785f6772616e740872656a6563746564057469746c65086475726174696f6e0c746f74616c5f6772616e7473311823124001f13119231240003b31198105124000010031002b641244320481021244b122b2103209b20923b201b3320a730035013500286427091228642a121134002312114422433204810312361a00800f4170706c7920666f72206772616e74121040014e31002b6412361a008019417070726f7665206772616e74206170706c69636174696f6e12104000d0361a00801852656a656374206772616e74206170706c69636174696f6e1240009531002b6412361a00800a45646974204772616e741210400046361a00801d417070726f76652f52656a656374204772616e742062792041646d696e1240000100361a0117221240000b28642a124428270967224328642a124428270467224328642a1244270a361a0167270b361a0217672707361a0317672708361a041767270c361a0517672705361a06176729361a0717672243286427041244b124b210363201b218361a01b21a23b201b32243286427041244361a041729640c44b124b210363201b218361a01b21a23b201b622b210361c01b207361a0217b20823b201b622b210361c02b207361a0317b20823b201b32706270664361a021708361a031708672243286427041244361a011729640c44361a021729640c44361a031729640c442705642706640d44361a02172705640e44361a02172707640f44361a02172708640e442243311b81091244270a361a0067270b361a0117672707361a0217672708361a031767270c361a0417672705361a05176729361a0617678003455347361a07176727062367282a672b361a08672243
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
main_l13:
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
byte 0x0620050001060502311822124003bb3119221240001331192512400001003100320912400001002343361a00800c437265617465204772616e7412400039361a00800c44656c657465204772616e741240000100b124b210363201b21825b21922b201b623b21081d0a323b2083209b20722b201b32343320421041244330010231244330110241244320a730035033502340244b124b2108103b2358108b23480ce05062003010006260d067374617475730e6772616e745f656e645f646174650770656e64696e670763726561746f7208617070726f7665640c746f74616c5f6275646765740b676976656e5f6772616e74096d696e5f6772616e74096d61785f6772616e740872656a6563746564057469746c65086475726174696f6e0c746f74616c5f6772616e7473311823124001f13119231240003b31198105124000010031002b641244320481021244b122b2103209b20923b201b3320a730035013500286427091228642a121134002312114422433204810312361a00800f4170706c7920666f72206772616e74121040014e31002b6412361a008019417070726f7665206772616e74206170706c69636174696f6e12104000d0361a00801852656a656374206772616e74206170706c69636174696f6e1240009531002b6412361a00800a45646974204772616e741210400046361a00801d417070726f76652f52656a656374204772616e742062792041646d696e1240000100361a0117221240000b28642a124428270967224328642a124428270467224328642a1244270a361a0167270b361a0217672707361a0317672708361a041767270c361a0517672705361a06176729361a0717672243286427041244b124b210363201b218361a01b21a23b201b32243286427041244361a041729640c44b124b210363201b218361a01b21a23b201b622b210361c01b207361a0217b20823b201b622b210361c02b207361a0317b20823b201b32706270664361a021708361a031708672243286427041244361a011729640c44361a021729640c44361a031729640c442705642706640d44361a02172705640e44361a02172707640f44361a02172708640e442243311b81091244270a361a0067270b361a0117672707361a0217672708361a031767270c361a0417672705361a05176729361a0617678003455347361a07176727062367282a672b361a08672243b21e800406810143b21f361a01b21a361a02b21a361a03b21a361a04b21a361a05b21a361a06b21a361a07b21a361a08b21a3100b21a22b21922b201b3b43d720835013500b123b2103400b207361a0617b20822b201b32343311b2104124480116f7267616e69736174696f6e5f6e616d65361a006780087573657274797065361a01672343
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
main_l14:
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
                               global_schema=global_schema, local_schema=local_schema, app_args=args_list)

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

    # minimum balance is 300_000 for creating grant manager by the grant creator
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


# creating grant by the grant creator and grant manager
def grant_app(client, user_app_id, title, duration, min_grant, max_grant,
              total_grants, total_budget, grant_end_date, ESG):

    # define the sender for the transactions
    print(f'Creating Grant by {user_app_id}...')
    sender = get_address_from_application(user_app_id)

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
def approve_grant_application(client, wallet_address, application_app_id, user_app_id, grant_app_id):

    # derive the accounts
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

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# approve milestone 1 by grant manager/creator
# user_app_id of the applicant
def milestone_1_approval(client, wallet_address, application_app_id, user_app_id):

    # derive the accounts
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

        txngrp = [{'txn': encoding.msgpack_encode(txn)}]

        return txngrp
    else:
        return ({'message': "Milestone 1 Deadline Reached"})


# approve milestone 2 by grant manager/creator
# user_app_id of the applicant
def milestone_2_approval(client, wallet_address, application_app_id, user_app_id):

    # derive the accounts
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

        txngrp = [{'txn': encoding.msgpack_encode(txn)}]

        return txngrp
    else:
        return ({'message': "Milestone 1 Deadline Reached"})


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
