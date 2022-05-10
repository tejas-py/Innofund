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
bnz main_l28
txn OnCompletion
int NoOp
==
bnz main_l15
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
bnz main_l12
txna ApplicationArgs 0
byte "update_details"
==
bnz main_l9
err
main_l9:
byte "title"
txna ApplicationArgs 1
app_global_put
byte "description"
txna ApplicationArgs 2
app_global_put
byte "category"
txna ApplicationArgs 3
app_global_put
byte "start_time"
txna ApplicationArgs 4
btoi
app_global_put
byte "end_time"
txna ApplicationArgs 5
btoi
app_global_put
byte "funding_category"
txna ApplicationArgs 6
app_global_put
byte "fund_limit"
txna ApplicationArgs 7
btoi
app_global_put
byte "reward_type"
txna ApplicationArgs 8
app_global_put
byte "country"
txna ApplicationArgs 9
app_global_put
byte "end_time"
app_global_get
byte "start_time"
app_global_get
>
bnz main_l11
err
main_l11:
int 1
return
main_l12:
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
bnz main_l14
err
main_l14:
byte "total_investment"
byte "total_investment"
app_global_get
txna ApplicationArgs 2
btoi
+
app_global_put
int 1
return
main_l15:
global GroupSize
int 2
==
txna ApplicationArgs 0
byte "Check"
==
&&
bnz main_l25
global GroupSize
int 2
==
txna ApplicationArgs 0
byte "Check_again"
==
&&
bnz main_l22
global GroupSize
int 2
==
txna ApplicationArgs 0
byte "No Check"
==
&&
bnz main_l21
txna ApplicationArgs 0
byte "Blocking/Rejecting Campaign"
==
bnz main_l20
err
main_l20:
int 1
return
main_l21:
int 1
return
main_l22:
txna ApplicationArgs 1
btoi
byte "end_time"
app_global_get
>
bnz main_l24
int 0
return
main_l24:
int 1
return
main_l25:
byte "end_time"
app_global_get
byte "start_time"
app_global_get
>
txna ApplicationArgs 1
btoi
byte "fund_limit"
app_global_get
<=
&&
byte "fund_limit"
app_global_get
byte "total_investment"
app_global_get
>=
&&
bnz main_l27
err
main_l27:
int 1
return
main_l28:
txn NumAppArgs
int 10
==
assert
byte "title"
txna ApplicationArgs 0
app_global_put
byte "description"
txna ApplicationArgs 1
app_global_put
byte "category"
txna ApplicationArgs 2
app_global_put
byte "start_time"
txna ApplicationArgs 3
btoi
app_global_put
byte "end_time"
txna ApplicationArgs 4
btoi
app_global_put
byte "funding_category"
txna ApplicationArgs 5
app_global_put
byte "fund_limit"
txna ApplicationArgs 6
btoi
app_global_put
byte "reward_type"
txna ApplicationArgs 7
app_global_put
byte "country"
txna ApplicationArgs 8
app_global_put
byte "total_investment"
txna ApplicationArgs 9
btoi
app_global_put
byte "end_time"
app_global_get
byte "start_time"
app_global_get
>
bnz main_l30
err
main_l30:
int 1
return
"""

# Declare clear state program source
clear_program_source = b"""#pragma version 5
int 1
"""


# Create new campaign
def create_app(client, your_passphrase, title, description,
               category, start_time, end_time, fund_category,
               fund_limit, reward_type, country):
    print("Creating application...")

    approval_program = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)

    # Fetching public and private address from the passphrase, passed as argument.
    private_key = mnemonic.to_private_key(your_passphrase)
    address = account.address_from_private_key(private_key)

    account_info = client.account_info(address)
    print("Account balance: {} microAlgos".format(account_info.get('amount')) + "\n")

    sender = address
    on_complete = OnComplete.NoOpOC.real

    params = client.suggested_params()

    # params.flat_fee = True
    # params.fee = 2000

    # investment in the campaign at the time of creation
    investment = 0

    args_list = [bytes(title, 'utf8'), bytes(description, 'utf8'), bytes(category, 'utf8'),
                 int(start_time), int(end_time), bytes(fund_category, 'utf8'),
                 int(fund_limit), bytes(reward_type, 'utf-8'), bytes(country, 'utf8'), int(investment)]

    txn = ApplicationCreateTxn(sender=sender, sp=params, on_complete=on_complete,
                               approval_program=approval_program, clear_program=clear_program,
                               global_schema=global_schema, local_schema=local_schema, app_args=args_list,
                               note="Campaign")

    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    client.send_transactions([signed_txn])
    com_func.wait_for_confirmation(client, tx_id)
    transaction_response = client.pending_transaction_info(tx_id)
    campaign_id = transaction_response['application-index']
    print("Created new Campaign ID: ", campaign_id)

    return string(campaign_id)


# Transfer NFT to creator from Admin
def admin_creator(client, admin_passphrase, asset_id, creator_passphrase, amount):
    # define address from private key of creator
    admin_private_key = mnemonic.to_private_key(admin_passphrase)
    admin_account = account.address_from_private_key(admin_private_key)

    campaign_creator_private_key = mnemonic.to_private_key(creator_passphrase)
    creator_address = account.address_from_private_key(campaign_creator_private_key)


# set suggested params
    params = client.suggested_params()

    # Use the AssetTransferTxn class to transfer assets and opt-in: Transaction 1
    txn_1 = AssetTransferTxn(
        sender=creator_address,
        sp=params,
        receiver=creator_address,
        amt=0,
        index=asset_id)
    print("Created Transaction 1: ", txn_1.get_txid())

    # Transferring NFT from admin to campaign creator: Transaction 2
    txn_2 = AssetTransferTxn(sender=admin_account,
                             sp=params,
                             receiver=creator_address,
                             amt=amount,
                             index=asset_id)
    print("Created Transaction 2: ", txn_2.get_txid())

    # Changing Manager of NFT: Transaction 3
    txn_3 = AssetConfigTxn(sender=admin_account, sp=params, index=asset_id,
                           manager=creator_address, reserve=creator_address,
                           freeze=creator_address, clawback=creator_address)
    print("Created Transaction 3: ", txn_3.get_txid())

    # grouping both the txn to give the group id
    print("Grouping Transactions...")
    group_id = transaction.calculate_group_id([txn_1, txn_2, txn_3])
    print("groupID of the Transaction: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id
    txn_3.group = group_id

    # split transaction group
    print("Splitting unsigned transaction group...")

    stxn_1 = txn_1.sign(campaign_creator_private_key)
    print("Creator signed txn_1: ", stxn_1.get_txid())

    stxn_2 = txn_2.sign(admin_private_key)
    print("Creator signed txn_2: ", stxn_2.get_txid())

    stxn_3 = txn_3.sign(admin_private_key)
    print("Creator signed txn_3: ", stxn_3.get_txid())

    # grouping the sign transactions
    signedGroup = [stxn_1, stxn_2, stxn_3]

    # send transactions
    print("Sending transaction group...")
    tx_id = client.send_transactions(signedGroup)

    # wait for confirmation
    com_func.wait_for_confirmation(client, tx_id)

    return "Transfer successful with transaction id: {} ".format(tx_id)


# Campaign call and freeze nft
def call_nft(client, campaign_creator_passphrase, asset_id, campaign_id):
    # define address from private key of creator
    creator_private_key = mnemonic.to_private_key(campaign_creator_passphrase)
    creator_account = account.address_from_private_key(creator_private_key)

    # set suggested params
    params = client.suggested_params()

    # Campaign application call: transaction 1
    app_arg = ["No Check"]
    txn_1 = ApplicationNoOpTxn(creator_account, params, campaign_id, app_arg)
    print("Created Transaction 1: ", txn_1.get_txid())

    # NFT Freeze: transaction 2
    txn_2 = AssetFreezeTxn(
        sender=creator_account,
        sp=params,
        index=asset_id,
        target=creator_account,
        new_freeze_state=True
    )
    print("Created Transaction 2: ", txn_2.get_txid())
    # grouping both the txn to give the group id
    print("Grouping Transactions...")
    group_id = transaction.calculate_group_id([txn_1, txn_2])
    print("groupID of the Transaction: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id

    # split transaction group
    print("Splitting unsigned transaction group...")

    stxn_1 = txn_1.sign(creator_private_key)
    print("Investor signed txn_2: ", stxn_1.get_txid())

    stxn_2 = txn_2.sign(creator_private_key)
    print("Investor signed txn_3: ", stxn_2.get_txid())

    # grouping the sign transactions
    signedGroup = [stxn_1, stxn_2]

    # send transactions
    print("Sending transaction group...")
    tx_id = client.send_transactions(signedGroup)

    # wait for confirmation
    com_func.wait_for_confirmation(client, tx_id)

    return "Transfer successful with transaction id: {} ".format(tx_id)


# Transfer NFT from Campaign Creator to Investor
def nft_creator_investor(client, investor_passphrase, creator_passphrase, asset_id, asset_amount):
    # Getting private and public key of campaign creator
    creator_private_key = mnemonic.to_private_key(creator_passphrase)
    creator_address = account.address_from_private_key(creator_private_key)

    # getting private and public key of investor
    investor_private_key = mnemonic.to_private_key(investor_passphrase)
    investor_address = account.address_from_private_key(investor_private_key)

    # declaring parameters
    params = client.suggested_params()

    # Use the AssetTransferTxn class to transfer assets and opt-in
    txn_1 = AssetTransferTxn(
        sender=investor_address,
        sp=params,
        receiver=investor_address,
        amt=0,
        index=asset_id)
    stxn = txn_1.sign(investor_private_key)
    txid = client.send_transaction(stxn)
    print("Signed transaction with txID: {}".format(txid))
    # Wait for the transaction to be confirmed
    confirmed_txn = wait_for_confirmation(client, txid, 4)
    print("TXID: ", txid)
    print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))

    txn_2 = AssetTransferTxn(sender=creator_address,
                             sp=params,
                             receiver=investor_address,
                             amt=asset_amount,
                             index=asset_id)
    sign_txn = txn_2.sign(creator_private_key)
    tx_id = client.send_transaction(sign_txn)
    print("Signed transaction with txID: {}".format(tx_id))
    # Wait for the transaction to be confirmed
    confirmed_txn_2 = wait_for_confirmation(client, tx_id, 4)
    print("TXID: ", tx_id)
    print("Result confirmed in round: {}".format(confirmed_txn_2['confirmed-round']))
    return "Transaction successful with transaction id: {}".format(tx_id)


# Investors participate in the campaigns and invest
def call_app(client, your_passphrase, campaignID, investment):
    # Converting Passphrase to public and private key.
    investor_private_key = mnemonic.to_private_key(your_passphrase)
    investor_account = account.address_from_private_key(investor_private_key)

    escrow_account = "BJATCHES5YJZJ7JITYMVLSSIQAVAWBQRVGPQUDT5AZ2QSLDSXWWM46THOY"

    # get node suggested parameters
    params = client.suggested_params()

    # create transactions
    print("Creating transactions...")

    # Investor Account to call app.
    sender = investor_account
    args_list = ["Check", int(investment)]
    txn_1 = ApplicationNoOpTxn(sender, params, campaignID, args_list)
    print("Created Transaction: ", txn_1.get_txid())

    # Transaction from Investor Account to Escrow Account
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
    print("groupID of the Transaction: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id

    # split transaction group
    print("Splitting unsigned transaction group...")
    # this example does not use files on disk, so splitting is implicit above

    # split transaction group
    print("Splitting unsigned transaction group...")

    stxn_1 = txn_1.sign(investor_private_key)
    print("Investor signed txn_1: ", stxn_1.get_txid())

    stxn_2 = txn_2.sign(investor_private_key)
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


# update total investment of the campaign
def update_app(client, id_passphrase, app_id, investment):
    # declare sender
    update_private_key = mnemonic.to_private_key(id_passphrase)
    sender = account.address_from_private_key(update_private_key)

    approval_program = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)

    # define updated arguments
    app_args = ["update_investment", int(com_func.Today_seconds()), int(investment)]

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = ApplicationUpdateTxn(sender, params, app_id, approval_program, clear_program, app_args)

    # sign transaction
    signed_txn = txn.sign(update_private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation

    confirmed_txn = com_func.wait_for_confirmation(client, tx_id)
    print("TXID: ", tx_id)
    print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))
    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['txn']['txn']['apid']
    return string(app_id)


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
    args_list = ["Check_again", int(com_func.Today_seconds())]
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
def call_asset_destroy(client, creator_passphrase, asset_id, campaignID):

    # define address from private key of creator
    creator_private_key = mnemonic.to_private_key(creator_passphrase)
    creator_account = account.address_from_private_key(creator_private_key)

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

    # grouping both the txn to give the group id
    print("Grouping Transactions...")
    group_id = calculate_group_id([txn_1, txn_2])
    print("groupID of the Transaction: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id

    # split transaction group
    print("Splitting unsigned transaction group...")

    # signing the transactions
    stxn_1 = txn_1.sign(creator_private_key)
    print("Creator signed txn_1: ", stxn_1.get_txid())

    stxn_2 = txn_2.sign(creator_private_key)
    print("Creator signed txn_2: ", stxn_2.get_txid())

    # grouping the sign transactions
    signedGroup = [stxn_1, stxn_2]

    # send transactions
    print("Sending transaction group...")
    tx_id = client.send_transactions(signedGroup)

    # wait for confirmation
    com_func.wait_for_confirmation(client, tx_id)

    return string(tx_id)


# update existing details of the campaign
def update_campaign(client, id_passphrase, app_id, title, description,
                    category, start_time, end_time, fund_category,
                    fund_limit, reward_type, country):
    # declare sender
    update_private_key = mnemonic.to_private_key(id_passphrase)
    sender = account.address_from_private_key(update_private_key)

    approval_program = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)

    # define updated arguments
    app_args = ["update_details", bytes(title, 'utf8'), bytes(description, 'utf8'), bytes(category, 'utf8'),
                int(start_time), int(end_time), bytes(fund_category, 'utf8'),
                int(fund_limit), bytes(reward_type, 'utf-8'), bytes(country, 'utf8')]

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = ApplicationUpdateTxn(sender, params, app_id, approval_program, clear_program, app_args)

    # sign transaction
    signed_txn = txn.sign(update_private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation

    confirmed_txn = com_func.wait_for_confirmation(client, tx_id)
    print("TXID: ", tx_id)
    print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))
    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['txn']['txn']['apid']
    return string(app_id)


# Reason for blocking/rejecting Campaign
def block_reason(client, passphrase, campaign_id, reason):
    # declaring the sender
    private_key = mnemonic.to_private_key(passphrase)
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()

    app_args = ["Blocking/Rejecting Campaign"]

    # create unsigned transaction
    txn = ApplicationNoOpTxn(sender, params, campaign_id, app_args, note=reason)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    confirmed_txn = wait_for_confirmation(client, tx_id, 4)
    print("TXID: ", tx_id)
    print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))
    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['txn']['txn']['apid']

    return app_id


# delete campaign and unfreeze NFT
def nft_delete(client, creator_passphrase, campaign_id, asset_id):
    # define address from private key of creator
    creator_private_key = mnemonic.to_private_key(creator_passphrase)
    creator_account = account.address_from_private_key(creator_private_key)

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
    print("Created Transaction 1: ", txn_1.get_txid())

    # delete campaign: Transaction 2
    txn_2 = ApplicationDeleteTxn(creator_account, params, campaign_id)
    print("Created Transaction 2: ", txn_2.get_txid())

    # grouping both the txn to give the group id
    print("Grouping Transactions...")
    group_id = calculate_group_id([txn_1, txn_2])
    print("groupID of the Transaction: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id

    # split transaction group
    print("Splitting unsigned transaction group...")

    # signing the transactions
    stxn_1 = txn_1.sign(creator_private_key)
    print("Creator signed txn_1: ", stxn_1.get_txid())

    stxn_2 = txn_2.sign(creator_private_key)
    print("Creator signed txn_2: ", stxn_2.get_txid())

    # grouping the sign transactions
    signedGroup = [stxn_1, stxn_2]

    # send transactions
    print("Sending transaction group...")
    tx_id = client.send_transactions(signedGroup)

    # wait for confirmation
    com_func.wait_for_confirmation(client, tx_id)

    return string(tx_id)
