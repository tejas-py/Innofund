from algosdk import mnemonic
from algosdk.future.transaction import *
from billiard.five import string
import utilities.CommonFunctions as com_func
from utilities.CommonFunctions import Today_seconds

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
bnz main_l24
txn OnCompletion
int NoOp
==
bnz main_l13
txn OnCompletion
int UpdateApplication
==
bnz main_l4
err
main_l4:
txna ApplicationArgs 0
byte "update_investment"
==
bnz main_l10
txna ApplicationArgs 0
byte "update_details"
==
bnz main_l7
err
main_l7:
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
bnz main_l9
err
main_l9:
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
bnz main_l21
global GroupSize
int 2
==
txna ApplicationArgs 0
byte "Check_again"
==
&&
bnz main_l18
global GroupSize
int 4
==
txna ApplicationArgs 0
byte "No Check"
==
&&
bnz main_l17
err
main_l17:
int 1
return
main_l18:
txna ApplicationArgs 1
btoi
byte "end_time"
app_global_get
>
bnz main_l20
int 0
return
main_l20:
int 1
return
main_l21:
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
bnz main_l23
err
main_l23:
int 1
return
main_l24:
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
bnz main_l26
err
main_l26:
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


# Campaign call and Transfer NFT to creator from Admin
def call_nft_transfer(client, admin_passphrase, asset_id, campaignID, creator_passphrase, amount):
    # define address from private key of creator
    creator_private_key = mnemonic.to_private_key(admin_passphrase)
    creator_account = account.address_from_private_key(creator_private_key)

    campaign_creator_private_key = mnemonic.to_private_key(creator_passphrase)

    # get the campaign creator address from the campaign id
    campaign_creator_address = com_func.get_address_from_application(campaignID)

    # set suggested params
    params = client.suggested_params()

    args = ["No Check"]

    print("Calling Campaign Application...")

    # creator to call app(campaign): transaction 1
    sender = creator_account
    txn_1 = ApplicationNoOpTxn(sender, params, campaignID, args)
    print("Created Transaction 1: ", txn_1.get_txid())

    # Use the AssetTransferTxn class to transfer assets and opt-in: Transaction 2
    txn_2 = AssetTransferTxn(
        sender=campaign_creator_address,
        sp=params,
        receiver=campaign_creator_address,
        amt=0,
        index=asset_id)
    print("Created Transaction 2: ", txn_2.get_txid())

    # Minting NFT: Transaction 3
    txn_3 = AssetTransferTxn(sender=creator_account,
                             sp=params,
                             receiver=campaign_creator_address,
                             amt=amount,
                             index=asset_id)
    print("Created Transaction 3: ", txn_3.get_txid())

    # Changing Manager of NFT: Transaction 4
    txn_4 = AssetConfigTxn(sender=creator_account, sp=params, index=asset_id,
                           manager=campaign_creator_address, reserve=campaign_creator_address,
                           freeze=campaign_creator_address, clawback=campaign_creator_address)
    print("Created Transaction 4: ", txn_4.get_txid())

# grouping both the txn to give the group id
    print("Grouping Transactions...")
    group_id = transaction.calculate_group_id([txn_1, txn_2, txn_3, txn_4])
    print("groupID of the Transaction: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id
    txn_3.group = group_id
    txn_4.group = group_id

    # split transaction group
    print("Splitting unsigned transaction group...")

    # signing the transactions
    stxn_1 = txn_1.sign(creator_private_key)
    print("Investor signed txn_1: ", stxn_1.get_txid())

    stxn_2 = txn_2.sign(campaign_creator_private_key)
    print("Investor signed txn_2: ", stxn_2.get_txid())

    stxn_3 = txn_3.sign(creator_private_key)
    print("Investor signed txn_3: ", stxn_3.get_txid())

    stxn_4 = txn_4.sign(creator_private_key)
    print("Investor signed txn_3: ", stxn_4.get_txid())

    # grouping the sign transactions
    signedGroup = [stxn_1, stxn_2, stxn_3, stxn_4]

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
    app_args = ["update_investment", int(Today_seconds()), int(investment)]

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
    args_list = ["Check_again", int(Today_seconds())]
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
