from algosdk import mnemonic
from algosdk.future.transaction import *
from billiard.five import string
import utilities.CommonFunctions as com_func

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
txna ApplicationArgs 1
btoi
byte "fund_limit"
app_global_get
byte "total_investment"
app_global_get
-
<=
bnz main_l12
err
main_l12:
byte "total_investment"
byte "total_investment"
app_global_get
txna ApplicationArgs 1
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
