# This transaction contains:
# 1. Create new campaign and storing the data (Create application transaction).
# 2. Group transaction: (Campaign application call and NFT transfer from Admin to Campaign creator).
# 3. Transfer NFT from Campaign Creator to Investor (group transaction: opt-in NFT by investor and transfer NFT).
# 4. Investors participate in the campaigns and invest (Campaign Application update transaction).
# 5. Update the total investment of the campaign (Update Campaign app transaction).
# 6. Creator pulls out the investment done in that campaign whenever the campaign is over.
# 7. Group transaction of (Campaign App call and burn asset by campaign creator).
# 8. Update the campaign app with new details of campaign (Campaign update application transaction).
# 9. Add reason for Campaign to block/reject.

from algosdk import mnemonic
from algosdk.future.transaction import *
from billiard.five import string
import utilities.CommonFunctions as com_func

# Declare application state storage (immutable)
local_ints = 1
local_bytes = 1
global_ints = 20
global_bytes = 20
global_schema = StateSchema(global_ints, global_bytes)
local_schema = StateSchema(local_ints, local_bytes)

# Declare the approval program source
approval_program_source_initial = b"""#pragma version 5
txn ApplicationID
int 0
==
bnz main_l26
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
txna ApplicationArgs 0
byte "update_investment"
==
bnz main_l10
txna ApplicationArgs 0
byte "update_details"
==
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
byte "reward_type"
txna ApplicationArgs 6
app_global_put
byte "country"
txna ApplicationArgs 7
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
byte "Check"
==
&&
bnz main_l23
global GroupSize
int 2
==
txna ApplicationArgs 0
byte "Check if the campaign has ended."
==
&&
bnz main_l20
global GroupSize
int 2
==
txna ApplicationArgs 0
byte "No Check"
==
&&
bnz main_l19
txna ApplicationArgs 0
byte "Blocking/Rejecting Campaign"
==
bnz main_l18
err
main_l18:
int 1
return
main_l19:
int 1
return
main_l20:
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
bnz main_l22
int 0
return
main_l22:
int 1
return
main_l23:
txna ApplicationArgs 1
btoi
byte "fund_limit"
app_global_get
<=
byte "fund_limit"
app_global_get
byte "total_investment"
app_global_get
>=
&&
bnz main_l25
err
main_l25:
int 1
return
main_l26:
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
bnz main_l28
err
main_l28:
int 1
return
"""

# Declare clear state program source
clear_program_source = b"""#pragma version 5
int 1
"""


# Create new campaign
def create_campaign_app(client, public_address, title,
                        category, end_time, fund_category, fund_limit,
                        reward_type, country):
    print("Creating campaign application...")

    approval_program = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)

    # Declaring sender
    sender = public_address

    on_complete = OnComplete.NoOpOC.real
    params = client.suggested_params()

    # investment in the campaign at the time of creation
    investment = 0

    args_list = [bytes(title, 'utf8'), bytes(category, 'utf8'),
                 int(end_time), bytes(fund_category, 'utf8'),
                 int(fund_limit), bytes(reward_type, 'utf-8'), bytes(country, 'utf8'), int(investment)]

    txn = ApplicationCreateTxn(sender=sender, sp=params, on_complete=on_complete,
                               approval_program=approval_program, clear_program=clear_program,
                               global_schema=global_schema, local_schema=local_schema, app_args=args_list,
                               note="Campaign")

    txngrp = []
    txngrp.append({'txn': encoding.msgpack_encode(txn)})
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

    txngrp = []
    txngrp.append({'txn': encoding.msgpack_encode(txn)})

    return txngrp


# Transfer NFT to creator from Admin
def admin_creator(client, asset_id, amount, admin_account, creator_address):

    print(f"Transferring {asset_id} NFT...")

    # set suggested params
    params = client.suggested_params()

    # Transferring NFT from admin to campaign creator: Transaction 1
    txn = AssetTransferTxn(sender=admin_account,
                           sp=params,
                           receiver=creator_address,
                           amt=amount,
                           index=asset_id)

    txngrp = []
    txngrp.append({'txn': encoding.msgpack_encode(txn)})

    return txngrp


# Campaign call and freeze nft
def call_nft(client, asset_id, campaign_id):

    print(f"Assigning {asset_id} NFT to {campaign_id} Campaign...")
    # define address from private key of creator
    creator_account = com_func.get_address_from_application(campaign_id)

    # set suggested params
    params = client.suggested_params()

    # Campaign application call: transaction 1
    app_arg = ["No Check"]
    txn_1 = ApplicationNoOpTxn(creator_account, params, campaign_id, app_arg)

    # NFT Freeze: transaction 2
    txn_2 = AssetFreezeTxn(
        sender=creator_account,
        sp=params,
        index=asset_id,
        target=creator_account,
        new_freeze_state=True
    )

    print("Grouping transactions...")
    # compute group id and put it into each transaction
    group_id = transaction.calculate_group_id([txn_1, txn_2])
    print("...computed groupId: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id

    txngrp = []
    txngrp.append({'txn': encoding.msgpack_encode(txn_1)})
    txngrp.append({'txn': encoding.msgpack_encode(txn_2)})

    return txngrp


# Transfer NFT from Campaign Creator to Investor
def nft_creator_investor(client, creator_address, investor_address, asset_id, asset_amount):

    print(f"Transfering {asset_id} NFT to {investor_address}")

    # declaring parameters
    params = client.suggested_params()

    # unfreeze NFT
    txn_1 = AssetFreezeTxn(sender=creator_address, sp=params, index=asset_id,
                           target=creator_address, new_freeze_state=False)

    # Change Manager
    txn_2 = AssetConfigTxn(sender=creator_address, sp=params, index=asset_id,
                           manager=investor_address, reserve=investor_address,
                           freeze=investor_address, clawback=investor_address)

    # transaction from creator to investor
    txn_3 = AssetTransferTxn(sender=creator_address, sp=params, receiver=investor_address,
                             amt=asset_amount, index=asset_id)

    print("Grouping transactions...")
    # compute group id and put it into each transaction
    group_id = transaction.calculate_group_id([txn_1, txn_2, txn_3])
    print("...computed groupId: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id
    txn_3.group = group_id

    txngrp = []
    txngrp.append({'txn': encoding.msgpack_encode(txn_1)})
    txngrp.append({'txn': encoding.msgpack_encode(txn_2)})
    txngrp.append({'txn': encoding.msgpack_encode(txn_3)})
    return txngrp


# Investors participate in the campaigns and invest
def update_call_app(client, campaignID, investment, investor_account):

    print(f"Investing in {campaignID}...")

    escrow_account = "BJATCHES5YJZJ7JITYMVLSSIQAVAWBQRVGPQUDT5AZ2QSLDSXWWM46THOY"

    # get node suggested parameters
    params = client.suggested_params()

    # create transactions
    print("Creating transactions...")

    # Investor Account to call campaign app: Transaction 1
    sender = investor_account
    args_list = ["Check", int(investment)]
    txn_1 = ApplicationNoOpTxn(sender, params, campaignID, args_list)
    print("Created Transaction: ", txn_1.get_txid())

    # Transaction from Investor Account to Escrow Account: Transaction 2
    sender = investor_account
    receiver = escrow_account
    amount = investment
    txn_2 = PaymentTxn(sender, params, receiver, amount)
    print("Transaction 2 : from {} to {} for {} microAlgos".format(
        sender, receiver, amount))
    print("Created Transaction 2: ", txn_2.get_txid())

    print("Grouping transactions...")
    # compute group id and put it into each transaction
    group_id = transaction.calculate_group_id([txn_1, txn_2])
    print("...computed groupId: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id

    txngrp = []
    txngrp.append({'txn': encoding.msgpack_encode(txn_1)})
    txngrp.append({'txn': encoding.msgpack_encode(txn_2)})

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

    txngrp = []
    txngrp.append({'txn': encoding.msgpack_encode(txn)})

    return txngrp


# Creator pulls out the investment done in that campaign whenever the campaign is over
def pull_investment(client, creator_passphrase, campaignID, pull):
    # Converting Passphrase to public and private key.
    creator_private_key = mnemonic.to_private_key(creator_passphrase)
    creator_account = account.address_from_private_key(creator_private_key)

    # get node suggested parameters
    params = client.suggested_params()

    # create transactions
    print("Creating transactions...")

    # Creator Account to call app.
    sender = creator_account
    args_list = ["Check if the campaign has ended.", int(com_func.Today_seconds())]
    txn_1 = ApplicationNoOpTxn(sender, params, campaignID, args_list)
    print("Created Transaction: ", txn_1.get_txid())

    # Transaction from Escrow account to Creator Account
    # Logic Sign
    myprogram = "D:\webmob\Innofund_new\escrow_account\sample.teal"

    data = com_func.load_resource(myprogram)
    source = data.decode('utf-8')
    response = client.compile(source)
    programstr = response['result']
    t = programstr.encode("ascii")
    program = base64.decodebytes(t)
    lsig = LogicSigAccount(program)

    sender = lsig.address()
    receiver = creator_account
    amount = pull
    txn_2 = PaymentTxn(sender, params, receiver, amount)
    print("Transaction 2 : from {} to {} for {} microAlgos".format(
        sender, receiver, amount))
    print("Created Transaction 2: ", txn_2.get_txid())

    print("Grouping transactions...")
    # compute group id and put it into each transaction
    group_id = transaction.calculate_group_id([txn_1, txn_2])
    print("groupID of the Transaction: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id

    # split transaction group
    print("Splitting unsigned transaction group...")
    # this example does not use files on disk, so splitting is implicit above

    # sign transactions
    print("Signing transactions...")

    stxn_1 = txn_1.sign(creator_private_key)
    print("Investor signed txn_1: ", stxn_1.get_txid())

    stxn_2 = LogicSigTransaction(txn_2, lsig)
    print("Investor signed txn_2: ", stxn_2.get_txid())

    # assemble transaction group
    print("Assembling transaction group...")
    signedGroup = [stxn_1, stxn_2]

    # send transactions
    print("Sending transaction group...")
    tx_id = client.send_transactions(signedGroup)

    # wait for confirmation
    com_func.wait_for_confirmation(client, tx_id)

    return string(tx_id)


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

    txngrp = []
    txngrp.append({'txn_1': encoding.msgpack_encode(txn_1)})
    txngrp.append({'txn_2': encoding.msgpack_encode(txn_2)})

    return txngrp


# update existing details of the campaign
def update_campaign(client, public_address, app_id, title,
                    category, end_time, fund_category,
                    fund_limit, reward_type, country):
    print("Updating existing campaign....")
    # declare sender
    sender = public_address

    approval_program = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)

    # define updated arguments
    app_args = ["update_details", bytes(title, 'utf8'), bytes(category, 'utf8'),
                int(end_time), bytes(fund_category, 'utf8'),
                int(fund_limit), bytes(reward_type, 'utf-8'), bytes(country, 'utf8')]

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = ApplicationUpdateTxn(sender, params, app_id, approval_program, clear_program, app_args)

    txngrp = []
    txngrp.append({'txn': encoding.msgpack_encode(txn)})

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

    txngrp = []
    txngrp.append({'txn': encoding.msgpack_encode(txn)})

    return txngrp


# delete campaign and unfreeze NFT
def nft_delete(client, campaign_id, asset_id):

    print(f"Deleting {campaign_id} Campaign and unfreezing {asset_id} NFT....")

    # define address from private key of creator
    creator_account = com_func.get_address_from_application(campaign_id)
    # set suggested params
    params = client.suggested_params()

    # unfreeze nft: Transaction 1
    txn_1 = AssetFreezeTxn(
        sender=creator_account,
        sp=params,
        index=asset_id,
        target=creator_account,
        new_freeze_state=False
    )

    # delete campaign: Transaction 2
    txn_2 = ApplicationDeleteTxn(creator_account, params, campaign_id)

    print("Grouping transactions...")
    # compute group id and put it into each transaction
    group_id = transaction.calculate_group_id([txn_1, txn_2])
    print("...computed groupId: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id

    txngrp = []
    txngrp.append({'txn': encoding.msgpack_encode(txn_1)})
    txngrp.append({'txn': encoding.msgpack_encode(txn_2)})

    return txngrp
