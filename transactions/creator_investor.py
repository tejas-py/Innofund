from algosdk.future.transaction import *
import utilities.CommonFunctions as com_func
import transactions.indexer

# Declare application state storage (immutable)
local_ints = 5
local_bytes = 5
global_ints = 20
global_bytes = 20
global_schema = StateSchema(global_ints, global_bytes)
local_schema = StateSchema(local_ints, local_bytes)

# Declare the approval program source
approval_program_source_initial = b"""#pragma version 6
txn ApplicationID
int 0
==
bnz main_l38
txn OnCompletion
int NoOp
==
bnz main_l13
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
global GroupSize
int 2
==
txna ApplicationArgs 0
byte "update_investment"
==
&&
bnz main_l10
global GroupSize
int 4
==
txna ApplicationArgs 0
byte "update_details"
==
&&
bnz main_l9
err
main_l9:
byte "title"
txna ApplicationArgs 1
app_global_put
byte "category"
txna ApplicationArgs 2
app_global_put
byte "end_time"
txna ApplicationArgs 3
btoi
app_global_put
byte "funding_category"
txna ApplicationArgs 4
app_global_put
byte "fund_limit"
txna ApplicationArgs 5
btoi
app_global_put
byte "country"
txna ApplicationArgs 6
app_global_put
int 1
return
main_l10:
txna ApplicationArgs 2
btoi
byte "fund_limit"
app_global_get
byte "total_investment"
app_global_get
-
<=
byte "end_time"
app_global_get
txna ApplicationArgs 1
btoi
>
&&
bnz main_l12
err
main_l12:
byte "total_investment"
byte "total_investment"
app_global_get
txna ApplicationArgs 2
btoi
+
app_global_put
int 1
return
main_l13:
global GroupSize
int 2
==
txna ApplicationArgs 0
byte "Check if the campaign has ended."
==
&&
bnz main_l35
global GroupSize
int 2
==
txna ApplicationArgs 0
byte "No Check"
==
&&
bnz main_l34
global GroupSize
int 1
==
txna ApplicationArgs 0
byte "Blocking/Rejecting Campaign"
==
&&
bnz main_l33
global GroupSize
int 2
==
txn Sender
global CreatorAddress
==
&&
txna ApplicationArgs 0
byte "Send NFT to Campaign"
==
&&
bnz main_l30
global GroupSize
int 1
==
txna ApplicationArgs 0
byte "Send NFT to Investor"
==
&&
bnz main_l27
global GroupSize
int 5
==
txn Sender
global CreatorAddress
==
&&
txna ApplicationArgs 0
byte "Transfer NFT to Creator"
==
&&
bnz main_l24
global GroupSize
int 1
==
txna ApplicationArgs 0
byte "Milestone"
==
&&
bnz main_l21
err
main_l21:
txna ApplicationArgs 1
btoi
byte "end_time"
app_global_get
>
byte "fund_limit"
app_global_get
byte "total_investment"
app_global_get
==
||
bnz main_l23
int 0
return
main_l23:
itxn_begin
int pay
itxn_field TypeEnum
global CurrentApplicationAddress
itxn_field Sender
txna Accounts 1
itxn_field Receiver
txna ApplicationArgs 2
btoi
itxn_field Amount
int 0
itxn_field Fee
itxn_submit
int 1
return
main_l24:
txna ApplicationArgs 1
btoi
byte "end_time"
app_global_get
>
byte "fund_limit"
app_global_get
byte "total_investment"
app_global_get
==
||
bnz main_l26
int 0
return
main_l26:
itxn_begin
int axfer
itxn_field TypeEnum
txna Accounts 0
itxn_field AssetReceiver
int 1
itxn_field AssetAmount
txna Assets 0
itxn_field XferAsset
int 0
itxn_field Fee
itxn_submit
int 1
return
main_l27:
txna ApplicationArgs 1
btoi
byte "end_time"
app_global_get
>
byte "fund_limit"
app_global_get
byte "total_investment"
app_global_get
==
||
bnz main_l29
int 0
return
main_l29:
itxn_begin
int axfer
itxn_field TypeEnum
txn Sender
itxn_field AssetReceiver
txna ApplicationArgs 1
btoi
itxn_field AssetAmount
txna Assets 0
itxn_field XferAsset
int 0
itxn_field Fee
itxn_submit
int 1
return
main_l30:
txna ApplicationArgs 1
btoi
byte "end_time"
app_global_get
>
byte "fund_limit"
app_global_get
byte "total_investment"
app_global_get
==
||
bnz main_l32
int 0
return
main_l32:
itxn_begin
int axfer
itxn_field TypeEnum
global CurrentApplicationAddress
itxn_field AssetReceiver
int 0
itxn_field AssetAmount
txna Assets 0
itxn_field XferAsset
int 0
itxn_field Fee
itxn_submit
int 1
return
main_l33:
int 1
return
main_l34:
int 1
return
main_l35:
txna ApplicationArgs 1
btoi
byte "end_time"
app_global_get
>
byte "fund_limit"
app_global_get
byte "total_investment"
app_global_get
==
||
bnz main_l37
int 0
return
main_l37:
int 1
return
main_l38:
txn NumAppArgs
int 8
==
assert
byte "title"
txna ApplicationArgs 0
app_global_put
byte "category"
txna ApplicationArgs 1
app_global_put
byte "end_time"
txna ApplicationArgs 2
btoi
app_global_put
byte "funding_category"
txna ApplicationArgs 3
app_global_put
byte "fund_limit"
txna ApplicationArgs 4
btoi
app_global_put
byte "reward_type"
txna ApplicationArgs 5
app_global_put
byte "country"
txna ApplicationArgs 6
app_global_put
byte "total_investment"
txna ApplicationArgs 7
btoi
app_global_put
byte "end_time"
app_global_get
byte "start_time"
app_global_get
>
bnz main_l40
err
main_l40:
int 1
return
"""


# Declare the approval program source
approval_program_source_initial_milestone = b"""#pragma version 6
txn ApplicationID
int 0
==
bnz main_l20
txn OnCompletion
int NoOp
==
bnz main_l9
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
global GroupSize
int 4
==
txna ApplicationArgs 0
byte "update_details"
==
&&
bnz main_l8
err
main_l8:
byte "milestone_title"
txna ApplicationArgs 1
app_global_put
byte "milestone_number"
txna ApplicationArgs 2
btoi
app_global_put
byte "end_time"
txna ApplicationArgs 3
btoi
app_global_put
int 1
return
main_l9:
global GroupSize
int 2
==
txna ApplicationArgs 0
byte "start"
==
&&
bnz main_l17
global GroupSize
int 1
==
txna ApplicationArgs 0
byte "end"
==
&&
bnz main_l14
txna ApplicationArgs 0
byte "no_check"
==
bnz main_l13
err
main_l13:
int 1
return
main_l14:
txna ApplicationArgs 1
btoi
byte "end_time"
app_global_get
<=
bnz main_l16
err
main_l16:
int 1
return
main_l17:
txna ApplicationArgs 1
byte "milestone_title"
app_global_get
==
txna ApplicationArgs 2
btoi
byte "milestone_number"
app_global_get
==
&&
txna ApplicationArgs 3
btoi
byte "end_time"
app_global_get
<
&&
bnz main_l19
err
main_l19:
int 1
return
main_l20:
txn NumAppArgs
int 3
==
assert
byte "milestone_title"
txna ApplicationArgs 0
app_global_put
byte "milestone_number"
txna ApplicationArgs 1
btoi
app_global_put
byte "end_time"
txna ApplicationArgs 2
btoi
app_global_put
int 1
return
"""

# Declare clear state program source
clear_program_source = b"""#pragma version 6
int 1
"""


# Create new campaign
def create_campaign_app(client, public_address, title,
                        category, end_time, fund_category, fund_limit,
                        reward_type, country, milestone_title, milestone_number, end_time_milestone):
    print("Creating campaign application...")

    approval_program_campaign = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)
    approval_program_milestone = com_func.compile_program(client, approval_program_source_initial_milestone)

    # Declaring sender
    sender = public_address

    on_complete = OnComplete.NoOpOC.real
    params = client.suggested_params()

    # investment in the campaign at the time of creation
    investment = 0

    # create campaign application
    args_list = [bytes(title, 'utf8'), bytes(category, 'utf8'),
                 int(end_time), bytes(fund_category, 'utf8'),
                 int(fund_limit * 1_000_000), bytes(reward_type, 'utf-8'), bytes(country, 'utf8'), int(investment)]

    txn_1 = ApplicationCreateTxn(sender=sender, sp=params, on_complete=on_complete,
                                 approval_program=approval_program_campaign, clear_program=clear_program,
                                 global_schema=global_schema, local_schema=local_schema, app_args=args_list,
                                 note="Campaign")

    # create milestone 1 application
    milestone_args = [bytes(milestone_title[0], 'utf-8'), int(milestone_number[0]), int(end_time_milestone[0])]

    txn_2 = ApplicationCreateTxn(sender=sender, sp=params, on_complete=on_complete,
                                 approval_program=approval_program_milestone, clear_program=clear_program,
                                 global_schema=global_schema, local_schema=local_schema, app_args=milestone_args,
                                 note="milestone_1")

    # create milestone 2 application
    milestone_args = [bytes(milestone_title[1], 'utf-8'), int(milestone_number[1]), int(end_time_milestone[1])]

    txn_3 = ApplicationCreateTxn(sender=sender, sp=params, on_complete=on_complete,
                                 approval_program=approval_program_milestone, clear_program=clear_program,
                                 global_schema=global_schema, local_schema=local_schema, app_args=milestone_args,
                                 note="milestone_2")

    # create milestone 3 application
    milestone_args = [bytes(milestone_title[2], 'utf-8'), int(milestone_number[2]), int(end_time_milestone[2])]

    txn_4 = ApplicationCreateTxn(sender=sender, sp=params, on_complete=on_complete,
                                 approval_program=approval_program_milestone, clear_program=clear_program,
                                 global_schema=global_schema, local_schema=local_schema, app_args=milestone_args,
                                 note="milestone_3")

    print("Grouping transactions...")
    # compute group id and put it into each transaction
    group_id = transaction.calculate_group_id([txn_1, txn_2, txn_3, txn_4])
    print("...computed groupId: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id
    txn_3.group = group_id
    txn_4.group = group_id

    txngrp = [{'txn': encoding.msgpack_encode(txn_1)}, {'txn': encoding.msgpack_encode(txn_2)},
              {'txn': encoding.msgpack_encode(txn_3)}, {'txn': encoding.msgpack_encode(txn_4)}]

    return txngrp


# initiating milestone
def start_milestones(client, campaign_app_id, milestone_app_id, milestone_title, milestone_number):
    print("Starting the milestone...")

    sender = com_func.get_address_from_application(campaign_app_id)

    params = client.suggested_params()

    # call the campaign to see if the campaign has ended
    args_list_campaign = ["Check if the campaign has ended.", int(com_func.Today_seconds())]
    txn_1 = ApplicationNoOpTxn(sender, params, campaign_app_id, args_list_campaign)

    # call the milestone to start the application
    args_list_milestone = ['start', bytes(milestone_title, 'utf-8'), int(milestone_number), int(com_func.Today_seconds())]
    txn_2 = ApplicationNoOpTxn(sender, params, milestone_app_id, args_list_milestone, note="Milestone Started")

    print("Grouping transactions...")
    # compute group id and put it into each transaction
    group_id = transaction.calculate_group_id([txn_1, txn_2])
    print("...computed groupId: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id

    txngrp = [{'txn': encoding.msgpack_encode(txn_1)}, {'txn': encoding.msgpack_encode(txn_2)}]

    return txngrp


# end milestone
def end_milestone(client, milestone_app_id):

    print(f'Ending {milestone_app_id} milestone...')

    params = client.suggested_params()
    sender = com_func.get_address_from_application(milestone_app_id)

    # 100 days after the current date
    submission_time = com_func.Today_seconds() - 7948800
    app_args = ['end', int(submission_time)]

    txn = ApplicationNoOpTxn(sender, params, milestone_app_id, app_args, note="Milestone Ended")

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# reject milestone
def reject_milestone(client, note, milestone_app_id):
    print(f"Rejecting {milestone_app_id} milestone...")

    params = client.suggested_params()
    sender = com_func.get_address_from_application(milestone_app_id)
    app_args = ['no_check']

    txn = ApplicationNoOpTxn(sender, params, milestone_app_id, app_args, note=note)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# Opt-in to NFT
def opt_in(client, creator_address, asset_id):

    print(f"Opt-in {asset_id} Asset...")
    # set suggested params
    params = client.suggested_params()

    # Use the AssetTransferTxn class to transfer assets and opt-in
    txn = AssetTransferTxn(
        sender=creator_address,
        sp=params,
        receiver=creator_address,
        amt=0,
        index=asset_id)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# Transfer NFT to creator from Admin
def admin_creator(client, asset_id, amount, admin_account, creator_address):

    print(f"Transferring {asset_id} NFT...")

    # set suggested params
    params = client.suggested_params()

    # Transferring NFT from admin to campaign creator
    txn = AssetTransferTxn(sender=admin_account,
                             sp=params,
                             receiver=creator_address,
                             amt=amount,
                             index=asset_id)


    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# Campaign call and freeze nft
def nft_to_campaign(client, asset_id, campaign_id):

    print(f"Assigning {asset_id} NFT to {campaign_id} Campaign...")
    # define address from private key of creator
    creator_account = com_func.get_address_from_application(campaign_id)
    campaign_wallet_address = encoding.encode_address(encoding.checksum (b'appID' + campaign_id.to_bytes (8, 'big')))
    print("campaign wallet:", campaign_wallet_address)

    # set suggested params for transaction 1
    params_txn1 = client.suggested_params()
    params_txn1.fee = 1000
    params_txn1.flat_fee = True

    # payment to escrow account
    txn_1 = PaymentTxn(sender=creator_account, receiver=campaign_wallet_address, amt=100000, sp=params_txn1)

    # Campaign application call: transaction 1
    app_arg = ["Send NFT to Campaign"]
    asset_lst = [asset_id]
    txn_2 = ApplicationNoOpTxn(creator_account, params_txn1, campaign_id, app_arg, foreign_assets=asset_lst)
    # set suggested params for transaction 1
    params_txn2 = client.suggested_params()
    params_txn2.fee = 2000
    params_txn2.flat_fee = True

    # NFT transfer to campaign wallet address: transaction 2
    txn_3 = AssetTransferTxn(
        sender=creator_account,
        sp=params_txn2,
        receiver= campaign_wallet_address,
        amt=1,
        index=asset_id
    )

    print("Grouping transactions...")
    # compute group id and put it into each transaction
    group_id = transaction.calculate_group_id([txn_1, txn_2])
    print("...computed groupId: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id
    txn_3.group = group_id

    txngrp = [{'txn': encoding.msgpack_encode(txn_1)},
              {'txn': encoding.msgpack_encode(txn_2)},
              {'txn': encoding.msgpack_encode(txn_3)}]

    return txngrp


# Claiming NFT by Investor (the one who call this receives the NFT.)
def claim_nft(client, wallet_address, asset_id, asset_amount, campaign_app_id):

    print(f"Claiming {asset_id} NFT by {wallet_address}")

    # get node suggested parameters
    params_txn1 = client.suggested_params()
    params_txn1.fee = 1000
    params_txn1.flat_fee = True

    params_txn2 = client.suggested_params()
    params_txn2.fee = 2000
    params_txn2.flat_fee = True

    # define the arguments
    app_args_list = ["Send NFT to Investor", int(asset_amount)]
    asset_list = [asset_id]

    # Transaction 1: Opting to asset
    txn_1 = AssetTransferTxn(sender=wallet_address, receiver=wallet_address,
                             sp=params_txn1, amt=0, index=asset_id)


    # Transaction 2: Campaign Application Call
    txn_2 = ApplicationNoOpTxn(sender=wallet_address, sp=params_txn2, index=campaign_app_id,
                               app_args=app_args_list, foreign_assets=asset_list)

    print("Grouping transactions...")
    # compute group id and put it into each transaction
    group_id = transaction.calculate_group_id([txn_1, txn_2])
    print("...computed groupId: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id


    txngrp = [{'txn': encoding.msgpack_encode(txn_1)},
              {'txn': encoding.msgpack_encode(txn_2)}]

    return txngrp


# Investors participate in the campaigns and invest
def update_call_app(client, campaignID, investment, investor_account, meta_data):

    print(f"Investing in {campaignID}...")

    campaign_wallet_address = encoding.encode_address(encoding.checksum (b'appID' + campaignID.to_bytes (8, 'big')))

    # state the smart contract
    approval_program = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)

    # get node suggested parameters
    params = client.suggested_params()

    # declare the sender and receiver
    sender = investor_account
    receiver = campaign_wallet_address

    # Update the investment of the campaign application: Transaction 1
    app_args = ["update_investment", int(com_func.Today_seconds()), int(investment)]
    txn_1 = ApplicationUpdateTxn(sender, params, campaignID, approval_program, clear_program, app_args)

    # Transaction from Investor Account to Escrow Account: Transaction 2
    amount = int(investment)
    txn_2 = PaymentTxn(sender, params, receiver, amount, note=meta_data)

    print("Grouping transactions...")
    # compute group id and put it into each transaction
    group_id = transaction.calculate_group_id([txn_1, txn_2])
    txn_1.group = group_id
    txn_2.group = group_id

    txngrp = [{'txn': encoding.msgpack_encode(txn_1)},
              {'txn': encoding.msgpack_encode(txn_2)}]

    return txngrp


# update total investment of the campaign
def update_app(client, app_id, investment):

    print(f"Updating Investment in {app_id} Campaign...")
    # declare sender
    sender = com_func.get_address_from_application(app_id)

    approval_program = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)

    # define updated arguments
    app_args = ["update_investment", int(com_func.Today_seconds()), int(investment)]

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = ApplicationUpdateTxn(sender, params, app_id, approval_program, clear_program, app_args)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# Admin Approves the Milestone and send the investment to creator
def pull_investment(client, sender, campaign_app_id=None, milestone_number=None, milestone_app_id=None, note=None):

    # create transactions
    print("Creating transactions...")

    # get node suggested parameters
    params = client.suggested_params()
    params.fee = 2000
    params.flat_fee = True

    # get the total investment amount in campaign
    campaign_info = transactions.indexer.campaign(campaign_app_id)
    total_amount_in_campaign = campaign_info['totalInvested']

    creator_wallet_address = com_func.get_address_from_application(campaign_app_id)

    if milestone_number == 1:
        if transactions.indexer.check_payment_milestone(campaign_app_id) == "False":

            account_lst = [creator_wallet_address]
            args_list=["Milestone", int(com_func.Today_seconds()), int(total_amount_in_campaign / 3)]
            txn=ApplicationNoOpTxn(sender, params, campaign_app_id, args_list, note="Milestone 1 money, claimed", accounts=account_lst)

            txngrp=[{'txn':encoding.msgpack_encode(txn)}]
            return txngrp

        else:
            txngrp={"initial_payment_claimed":"TRUE"}
            return txngrp

    if milestone_number == 2:
        if transactions.indexer.check_payment_milestone(campaign_app_id) == "True":

            account_lst = [creator_wallet_address]
            args_list_2 = ["Milestone", int(com_func.Today_seconds()), int(total_amount_in_campaign / 3)]

            txn = ApplicationNoOpTxn(sender, params, campaign_app_id, args_list_2, accounts=account_lst, note="Milestone 2 money, claimed")

            txngrp = [{'txn':encoding.msgpack_encode(txn)}]
            return txngrp

        else:
            txngrp = {"Milestone Status":"Milestone 1 money has not been claimed yet"}
            return txngrp

    if milestone_number == 3:
        if transactions.indexer.check_payment_milestone_2(campaign_app_id) == "True":
            account_lst = [creator_wallet_address]

            args_list_3=["Milestone", int(com_func.Today_seconds()), int(total_amount_in_campaign / 3)]
            txn=ApplicationNoOpTxn(sender, params, campaign_app_id, args_list_3, note="Milestone 3 money, claimed", accounts=account_lst)

            txngrp=[{'txn':encoding.msgpack_encode(txn)}]
            return txngrp

        else:
            txngrp={"Milestone Status":"Milestone 2 has not been approved yet"}
            return txngrp

    else:
        if transactions.indexer.check_payment_milestone_3(campaign_app_id) == "True":
            txn=ApplicationNoOpTxn(sender, params, milestone_app_id, note=note)
            txngrp=[{'txn':encoding.msgpack_encode(txn)}]
            return txngrp

        else:
            txngrp={"Milestone Status":"Milestone 3 has not been approved yet"}
            return txngrp



def reject_milestones(client, sender, milestone_app_id, note):

    # get node suggested parameters
    params= client.suggested_params()

    txn=ApplicationNoOpTxn(sender, params, milestone_app_id, note=note)
    txngrp= [{'txn':encoding.msgpack_encode(txn)}]

    return txngrp


# Group transaction: (Campaign app call and Burn Asset)
def call_asset_destroy(client, asset_id, campaignID):

    # define address from private key of creator
    creator_account = com_func.get_address_from_application(campaignID)

    # set suggested params
    params = client.suggested_params()

    args = ["No Check"]

    print("Calling Campaign Application...")

    # creator to call app(campaign): transaction 1
    sender = creator_account
    txn_1 = ApplicationNoOpTxn(sender, params, campaignID, args)
    print("Created Transaction 1: ", txn_1.get_txid())

    # destroying asset: transaction 2
    txn_2 = AssetConfigTxn(sender=sender, sp=params, index=asset_id, strict_empty_address_check=False)
    print("Created Transaction 2: ", txn_2.get_txid())

    txngrp = [{'txn_1': encoding.msgpack_encode(txn_1)}, {'txn_2': encoding.msgpack_encode(txn_2)}]

    return txngrp


# update existing details of the campaign
def update_campaign(client, public_address, app_id, title,
                    category, end_time, fund_category,
                    fund_limit, country, milestone_id, milestones_title, milestone_number, milestone_end_time):
    print("Updating existing campaign....")
    # declare sender
    sender = public_address

    approval_program_campaign = com_func.compile_program(client, approval_program_source_initial)
    approval_program_milestone = com_func.compile_program(client, approval_program_source_initial_milestone)
    clear_program = com_func.compile_program(client, clear_program_source)

    # define updated arguments
    campaign = ["update_details", bytes(title, 'utf8'), bytes(category, 'utf8'),
                int(end_time), bytes(fund_category, 'utf8'),
                int(fund_limit * 1_000_000), bytes(country, 'utf8')]

    # get node suggested parameters
    params = client.suggested_params()

    # update campaign transaction
    txn_1 = ApplicationUpdateTxn(sender, params, app_id, approval_program_campaign, clear_program, campaign)

    # update milestones transactions
    milestone_1 = ["update_details", bytes(milestones_title[0], 'utf-8'), int(milestone_number[0]), int(milestone_end_time[0])]
    txn_2 = ApplicationUpdateTxn(sender, params, milestone_id[0], approval_program_milestone, clear_program, milestone_1)

    milestone_2 = ["update_details", bytes(milestones_title[1], 'utf-8'), int(milestone_number[1]), int(milestone_end_time[1])]
    txn_3 = ApplicationUpdateTxn(sender, params, milestone_id[1], approval_program_milestone, clear_program, milestone_2)

    milestone_3 = ["update_details", bytes(milestones_title[2], 'utf-8'), int(milestone_number[2]), int(milestone_end_time[2])]
    txn_4 = ApplicationUpdateTxn(sender, params, milestone_id[2], approval_program_milestone, clear_program, milestone_3)

    # compute group id and put it into each transaction
    print("Grouping transactions...")
    group_id = transaction.calculate_group_id([txn_1, txn_2, txn_3, txn_4])
    print("...computed groupId: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id
    txn_3.group = group_id
    txn_4.group = group_id

    txngrp = [{'txn': encoding.msgpack_encode(txn_1)},
              {'txn': encoding.msgpack_encode(txn_2)},
              {'txn': encoding.msgpack_encode(txn_3)},
              {'txn': encoding.msgpack_encode(txn_4)}]

    return txngrp


# Reason for blocking/rejecting Campaign
def block_reason(client, public_address, campaign_id, reason):

    print(f"Blocking/rejecting {campaign_id} campaign....")
    # declaring the sender
    sender = public_address

    # get node suggested parameters
    params = client.suggested_params()

    app_args = ["Blocking/Rejecting Campaign"]

    # create unsigned transaction
    txn = ApplicationNoOpTxn(sender, params, campaign_id, app_args, note=reason)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# delete campaign and unfreeze NFT
def nft_delete(client, campaign_id, asset_id, milestone_app_id):

    print(f"Deleting {campaign_id} Campaign, {milestone_app_id} milestones and transferring {asset_id} NFT....")

    # define address from private key of creator
    sender = com_func.get_address_from_application(campaign_id)

    # set suggested params
    params = client.suggested_params()

    # set params for transaction 1
    params_txn1 = client.suggested_params()
    params_txn1.fee = 2000
    params_txn1.flat_fee = True

    # transfer nft back to creator: Transaction 1
    args_list = ["Transfer NFT to Creator"]
    asset_list = [asset_id]
    txn_1 = ApplicationNoOpTxn(
        sender=sender, sp=params_txn1, index=campaign_id, app_args=args_list, foreign_assets=asset_list
    )

    # delete campaign: Transaction 2
    txn_2 = ApplicationDeleteTxn(sender, params, campaign_id)

    # delete milestones: transaction 3,4,5
    txn_3 = ApplicationDeleteTxn(sender, params, milestone_app_id[0])
    txn_4 = ApplicationDeleteTxn(sender, params, milestone_app_id[1])
    txn_5 = ApplicationDeleteTxn(sender, params, milestone_app_id[2])

    print("Grouping transactions...")
    # compute group id and put it into each transaction
    group_id = transaction.calculate_group_id([txn_1, txn_2, txn_3, txn_4, txn_5])
    print("...computed groupId: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id
    txn_3.group = group_id
    txn_4.group = group_id
    txn_5.group = group_id

    txngrp = [{'txn': encoding.msgpack_encode(txn_1)},
              {'txn': encoding.msgpack_encode(txn_2)},
              {'txn': encoding.msgpack_encode(txn_3)},
              {'txn': encoding.msgpack_encode(txn_4)},
              {'txn': encoding.msgpack_encode(txn_5)}]

    return txngrp
