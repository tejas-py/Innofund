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
bnz main_l16
txn OnCompletion
int NoOp
==
bnz main_l5
txn OnCompletion
int UpdateApplication
==
bnz main_l4
err
main_l4:
byte "fund_limit"
txna ApplicationArgs 0
btoi
app_global_put
int 1
return
main_l5:
global GroupSize
int 2
==
txna ApplicationArgs 0
byte "Check"
==
&&
bnz main_l13
global GroupSize
int 2
==
txna ApplicationArgs 0
byte "Check_again"
==
&&
bnz main_l10
global GroupSize
int 2
==
txna ApplicationArgs 0
byte "No Check"
==
&&
bnz main_l9
err
main_l9:
int 1
return
main_l10:
txna ApplicationArgs 1
btoi
byte "end_time"
app_global_get
>
bnz main_l12
int 0
return
main_l12:
int 1
return
main_l13:
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
bnz main_l15
err
main_l15:
int 1
return
main_l16:
txn NumAppArgs
int 9
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
byte "
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
    address = mnemonic.to_public_key(your_passphrase)

    account_info = client.account_info(address)
    print("Account balance: {} microAlgos".format(account_info.get('amount')) + "\n")

    sender = address
    on_complete = OnComplete.NoOpOC.real

    params = client.suggested_params()

    # params.flat_fee = True
    # params.fee = 2000

    args_list = [bytes(title, 'utf8'), bytes(description, 'utf8'), bytes(category, 'utf8'),
                 int(start_time), int(end_time), bytes(fund_category, 'utf8'),
                 int(fund_limit), bytes(reward_type, 'utf-8'), bytes(country, 'utf8')]

    txn = ApplicationCreateTxn(sender=sender, sp=params,on_complete=on_complete,
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


# Investors participate in the campaigns and invest
def call_app(client, your_passphrase, campaignID, investment):
    # Converting Passphrase to public and private key.
    investor_account = mnemonic.to_public_key(your_passphrase)
    investor_private_key = mnemonic.to_private_key(your_passphrase)

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


# update existing application
def update_app(client, id_passphrase, app_id, fund_limit):
    # declare sender
    update_private_key = mnemonic.to_private_key(id_passphrase)
    sender = account.address_from_private_key(update_private_key)

    approval_program = com_func.compile_program(client, approval_program_source_initial)
    clear_program = com_func.compile_program(client, clear_program_source)

    # define updated arguments
    app_args = [int(fund_limit)]

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
    creator_account = mnemonic.to_public_key(creator_passphrase)
    creator_private_key = mnemonic.to_private_key(creator_passphrase)

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
