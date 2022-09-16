from algosdk.future.transaction import *
from utilities.CommonFunctions import get_address_from_application, Today_seconds
from algosdk import encoding
from Contracts import user_contact, teal

# Declare application state storage (immutable)
local_ints = 0
local_bytes = 0
global_ints = 1
global_bytes = 1
global_schema = StateSchema(global_ints, global_bytes)
local_schema = StateSchema(local_ints, local_bytes)


# Generate a new account as well as new user id for each user that registers
def create_app(client, sender, usertype):

    print("Creating user application...")

    # import smart contract for the application
    approval_program = teal.to_teal(client, user_contact.approval_program())
    clear_program = teal.to_teal(client, user_contact.clearstate_contract())

    on_complete = OnComplete.NoOpOC.real

    params = client.suggested_params()

    args_list = [bytes(usertype, 'utf8')]

    txn = ApplicationCreateTxn(sender, params, on_complete,
                               approval_program, clear_program,
                               global_schema, local_schema, args_list)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# # Update User(Creator and Investor) details (User update application transaction)
# def update_user(client, user_id, name):
#     print("Updating existing user....")
#
#     approval_program = com_func.compile_program(client, approval_program_source_initial)
#     clear_program = com_func.compile_program(client, clear_program_source)
#
#     # declare sender
#     sender = get_address_from_application(user_id)
#
#     # get node suggested parameters
#     params = client.suggested_params()
#
#     app_args = [bytes(name, 'utf8')]
#
#     # create unsigned transaction
#     txn = ApplicationUpdateTxn(sender, params, user_id, approval_program, clear_program, app_args)
#
#     txngrp = [{'txn':encoding.msgpack_encode (txn)}]
#
#     return txngrp


# delete the user
def delete_user(client, user_id):

    print("Deleting {}..".format(user_id))

    # declare sender
    sender = get_address_from_application(user_id)

    # get node suggested parameters
    params = client.suggested_params()

    print("Doing Transaction...")
    # create unsigned transaction
    txn = ApplicationDeleteTxn(sender, params, user_id)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# delete campaign and milestones
def campaign_milestones(client, campaign_app_id, milestone_app_id):
    print(f"Deleting {campaign_app_id} campaign, and {milestone_app_id} milestones...")
    
    # declare sender
    sender = get_address_from_application(campaign_app_id)

    # get node suggested parameters
    params = client.suggested_params()

    print("Doing Transaction...")
    # deleting campaign 
    txn_1 = ApplicationDeleteTxn(sender, params, campaign_app_id, app_args=['Delete Campaign', int(Today_seconds())])

    # deleting milestones
    txn_2 = ApplicationDeleteTxn(sender, params, int(milestone_app_id[0]))
    txn_3 = ApplicationDeleteTxn(sender, params, int(milestone_app_id[1]))

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
