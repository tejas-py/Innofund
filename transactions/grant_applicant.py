from algosdk.future.transaction import *
from utilities.CommonFunctions import get_address_from_application, Today_seconds, compile_program

# Smart Contract of the Grant Creator
approval_program_source = b"""#pragma version 6
txn ApplicationID
int 0
==
bnz main_l12
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
global GroupSize
int 3
==
txna ApplicationArgs 0
byte "Create Grant Application"
==
&&
bnz main_l11
txna ApplicationArgs 0
byte "Delete Grant Application"
==
bnz main_l10
err
main_l10:
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
int 407000
itxn_field Amount
global CreatorAddress
itxn_field Receiver
int 0
itxn_field Fee
itxn_submit
int 1
return
main_l11:
txn Sender
global CreatorAddress
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
gtxn 2 TypeEnum
int appl
==
assert
itxn_begin
int appl
itxn_field TypeEnum
int 3
itxn_field GlobalNumByteSlice
int 2
itxn_field GlobalNumUint
byte 0x06200201002607067374617475730872656a65637465640770656e64696e6709636f6d706c657465640b6d696c6573746f6e655f310b6d696c6573746f6e655f320f7265717565737465645f66756e647331182312400156311923124000293119810512400001003100320912320481021210286429121028642a121028642b12104000010022433204810312361a0080184368616e67652073746174757320746f20617070726f766512104000f1361a0080194368616e67652073746174757320746f2072656a6563746564124000ca3100320912361a00801645646974204772616e74204170706c69636174696f6e121040008b361a008013417070726f7665204d696c6573746f6e6520311240005a361a008013417070726f7665204d696c6573746f6e6520321240002c361a00801052656a656374204d696c6573746f6e651240000100b122b210361c01b20923b201b32829672243b122b210361c01b20923b201b3282b672243b122b210361c01b207361a0117b20823b201b3224328642a12442704361a01672705361a02672706361a03176722432829672243288008617070726f766564672243311b81041244800c6772616e745f6170705f6964361a0017672704361a01672705361a02672706361a031767282a672243
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
int NoOp
itxn_field OnCompletion
int 0
itxn_field Fee
itxn_submit
int 1
return
main_l12:
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

# declare clear state program source
clear_program_source = b"""#pragma version 6
int 1
"""


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
    approval_program = compile_program(client, approval_program_source)
    clear_program = compile_program(client, clear_program_source)

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
