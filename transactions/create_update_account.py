# This transaction contains:
# 1. Create Account for new users (Create application transaction).
# 2. Update User(Creator and Investor) details (User update application transaction).
# 3. Delete existing user. (User application delete transaction)

from algosdk.future.transaction import *
import utilities.CommonFunctions as com_func
from algosdk import encoding

# Declare application state storage (immutable)
local_ints = 5
local_bytes = 5
global_ints = 5
global_bytes = 5
global_schema = StateSchema(global_ints, global_bytes)
local_schema = StateSchema(local_ints, local_bytes)

# Declare approval program source
approval_program_source_initial = b"""#pragma version 5
txn ApplicationID
int 0
==
bnz main_l12
txn OnCompletion
int NoOp
==
bnz main_l7
txn OnCompletion
int UpdateApplication
==
bnz main_l6
txn OnCompletion
int DeleteApplication
==
bnz main_l5
err
main_l5:
int 1
return
main_l6:
byte "name"
txna ApplicationArgs 0
app_global_put
int 1
return
main_l7:
global GroupSize
int 2
==
txna ApplicationArgs 0
byte "check_user"
==
&&
bnz main_l9
err
main_l9:
txna ApplicationArgs 1
byte "name"
app_global_get
==
txna ApplicationArgs 2
byte "usertype"
app_global_get
==
&&
bnz main_l11
err
main_l11:
int 1
return
main_l12:
txn NumAppArgs
int 3
==
assert
byte "name"
txna ApplicationArgs 0
app_global_put
byte "usertype"
txna ApplicationArgs 1
app_global_put
byte "email"
txna ApplicationArgs 2
app_global_put
int 1
return
"""

# Declare clear state program source
clear_program_source = b"""#pragma version 5
int 1
"""


# Generate a new account as well as new user id for each user that registers
def create_app(client, sender, name, usertype, email):
    print("Creating user application...")

    approval_program = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)

    on_complete = OnComplete.NoOpOC.real

    params = client.suggested_params()

    args_list = [bytes(name, 'utf8'), bytes(usertype, 'utf8'), bytes(email, 'utf8')]

    txn = ApplicationCreateTxn(sender, params, on_complete,
                               approval_program, clear_program,
                               global_schema, local_schema, args_list)

    txngrp = []
    txngrp.append({'txn': encoding.msgpack_encode(txn)})

    return txngrp


# Update User(Creator and Investor) details (User update application transaction)
def update_user(client, user_id, name):
    print("Updating existing user....")

    approval_program = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)

    # declare sender
    sender = com_func.get_address_from_application(user_id)

    # get node suggested parameters
    params = client.suggested_params()

    app_args = [bytes(name, 'utf8')]

    # create unsigned transaction
    txn = ApplicationUpdateTxn(sender, params, user_id, approval_program, clear_program, app_args)

    txngrp = []
    txngrp.append({'txn': encoding.msgpack_encode(txn)})

    return txngrp


# delete the user
def delete_user(client, user_id):

    print("Deleting {}..".format(user_id))

    # declare sender
    sender = com_func.get_address_from_application(user_id)

    # get node suggested parameters
    params = client.suggested_params()

    print("Doing Transaction...")
    # create unsigned transaction
    txn = ApplicationDeleteTxn(sender, params, user_id)

    txngrp = []
    txngrp.append({'txn': encoding.msgpack_encode(txn)})

    return txngrp

