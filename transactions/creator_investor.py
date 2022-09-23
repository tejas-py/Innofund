from algosdk.future.transaction import *
import API.connection
from utilities.CommonFunctions import get_address_from_application, Today_seconds
from transactions import indexer as index
from Contracts import campaign_contract, milestone_contract, teal

# Declare application state storage (immutable)
local_ints = 0
local_bytes = 0
global_ints = 15
global_bytes = 15
global_schema = StateSchema(global_ints, global_bytes)
local_schema = StateSchema(local_ints, local_bytes)

# connect to algorand client
algod_client = API.connection.algo_conn()


# Create new campaign
def create_campaign_app(client, public_address, title,
                        category, end_time, fund_category, fund_limit,
                        reward_type, country, ESG, milestone_title, milestone_number, end_time_milestone):
    print("Creating campaign application...")

    # import smart contract for the application
    approval_program_campaign = teal.to_teal(client, campaign_contract.approval_program())
    clear_program = teal.to_teal(client, campaign_contract.clearstate_contract())
    approval_program_milestone = teal.to_teal(client, milestone_contract.approval_program())

    # Declaring sender
    sender = public_address

    on_complete = OnComplete.NoOpOC.real
    params = client.suggested_params()

    # investment in the campaign at the time of creation
    investment = 0

    # create campaign application
    args_list = [bytes(title, 'utf8'), bytes(category, 'utf8'),
                 int(end_time), bytes(fund_category, 'utf8'),
                 int(fund_limit * 1_000_000), bytes(reward_type, 'utf-8'), bytes(country, 'utf8'), int(investment), int(ESG)]

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

    print("Grouping transactions...")

    # compute group id and put it into each transaction
    group_id = transaction.calculate_group_id([txn_1, txn_2, txn_3])
    print("...computed groupId: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id
    txn_3.group = group_id

    txngrp = [{'txn': encoding.msgpack_encode(txn_1)}, {'txn': encoding.msgpack_encode(txn_2)},
              {'txn': encoding.msgpack_encode(txn_3)}]

    return txngrp


# initiating milestone
def start_milestones(client, campaign_app_id, milestone_app_id, milestone_title, milestone_number):
    print("Starting the milestone...")

    sender = get_address_from_application(campaign_app_id)

    params = client.suggested_params()

    # call the campaign to see if the campaign has ended
    args_list_campaign = ["Check if the campaign has ended.", int(Today_seconds())]
    txn_1 = ApplicationNoOpTxn(sender, params, campaign_app_id, args_list_campaign)

    # call the milestone to start the application
    args_list_milestone = ['start', bytes(milestone_title, 'utf-8'), int(milestone_number), int(Today_seconds())]
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
    sender = get_address_from_application(milestone_app_id)

    # 100 days after the current date
    submission_time = Today_seconds() - 7948800
    app_args = ['end', int(submission_time)]

    txn = ApplicationNoOpTxn(sender, params, milestone_app_id, app_args, note="Milestone Ended")

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# reject milestone
# **************************
def reject_milestone(client, note, milestone_app_id):
    print(f"Rejecting {milestone_app_id} milestone...")

    params = client.suggested_params()
    sender = get_address_from_application(milestone_app_id)
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
    creator_account = get_address_from_application(campaign_id)
    campaign_wallet_address = encoding.encode_address(encoding.checksum(b'appID' + campaign_id.to_bytes(8, 'big')))
    print("campaign wallet:", campaign_wallet_address)

    # set suggested params for transaction 1
    params_txn1 = client.suggested_params()
    params_txn1.fee = 1000
    params_txn1.flat_fee = True

    # payment to escrow account: Transaction 1
    txn_1 = PaymentTxn(sender=creator_account, receiver=campaign_wallet_address, amt=200_000, sp=params_txn1)

    # Campaign application call: transaction 2
    app_arg = ["Send NFT to Campaign"]
    asset_lst = [asset_id]
    txn_2 = ApplicationNoOpTxn(creator_account, params_txn1, campaign_id, app_arg, foreign_assets=asset_lst)

    # set suggested params for transaction 3
    params_txn2 = client.suggested_params()
    params_txn2.fee = 2000
    params_txn2.flat_fee = True

    # NFT transfer to campaign wallet address: transaction 3
    txn_3 = AssetTransferTxn(
        sender=creator_account,
        sp=params_txn2,
        receiver=campaign_wallet_address,
        amt=1,
        index=asset_id
    )

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


# Claiming NFT by Investor (the one who call this receives the NFT.)
def claim_nft(client, user_app_id, asset_id, campaign_app_id):

    # top 10 investors in the campaign
    top_investors = index.list_investors(campaign_app_id)[:10]

    # check if the user has invested in the campaign
    for one_investor in top_investors:
        if one_investor['user_app_id'] == user_app_id:

            # get node suggested parameters
            params_txn1 = client.suggested_params()
            params_txn1.fee = 1000
            params_txn1.flat_fee = True

            params_txn2 = client.suggested_params()
            params_txn2.fee = 2000
            params_txn2.flat_fee = True

            # get the wallet address of the user
            wallet_address = get_address_from_application(user_app_id)

            # check if the user has claimed the nft
            asset_claim_info = index.check_claim_nft(user_app_id, campaign_app_id)

            if asset_claim_info[0]['can_claim_NFT'] == "True" and asset_claim_info[1]['claimed_nft'] == "False":

                # define the arguments
                app_args_list = ["Claim NFT", int(Today_seconds())]
                asset_list = [asset_id]

                # Transaction 1: Opting to asset
                txn_1 = AssetTransferTxn(sender=wallet_address, receiver=wallet_address,
                                         sp=params_txn1, amt=0, index=asset_id)

                # Transaction 2: Campaign Application Call
                txn_2 = ApplicationNoOpTxn(sender=wallet_address, sp=params_txn2, index=campaign_app_id,
                                           app_args=app_args_list, foreign_assets=asset_list, note="NFT Claimed")

                print("Grouping transactions...")
                # compute group id and put it into each transaction
                group_id = transaction.calculate_group_id([txn_1, txn_2])
                print("...computed groupId: ", group_id)
                txn_1.group = group_id
                txn_2.group = group_id

                txngrp = [{'txn': encoding.msgpack_encode(txn_1)},
                          {'txn': encoding.msgpack_encode(txn_2)}]

                return txngrp

            else:
                "User has claimed the NFT"

        else:
            "User is not the top 10 investor of the campaign."


# Investors participate in the campaigns and invest
def update_call_app(client, campaignID, investment, investor_account, meta_data):

    print(f"Investing in {campaignID}...")

    campaign_wallet_address = encoding.encode_address(encoding.checksum(b'appID' + campaignID.to_bytes(8, 'big')))

    # get node suggested parameters
    params = client.suggested_params()

    # declare the sender and receiver
    sender = investor_account
    receiver = campaign_wallet_address

    # Update the investment of the campaign application: Transaction 1
    app_args = ["update_investment", int(Today_seconds()), int(investment)]
    txn_1 = ApplicationNoOpTxn(sender, params, campaignID, app_args)

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
    sender = get_address_from_application(app_id)

    # define updated arguments
    app_args = ["update_investment", int(Today_seconds()), int(investment)]

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = ApplicationNoOpTxn(sender, params, app_id, app_args)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# Admin Approves the Milestone and send the investment to creator
def pull_investment(client, sender, campaign_app_id=None, milestone_number=None, milestone_app_id=None, approve_milestone_again=None):

    # create transactions
    print("Creating transactions...")

    # get node suggested parameters
    params = client.suggested_params()
    params.fee = 2000
    params.flat_fee = True

    # get the total investment amount in campaign
    print("he")
    campaign_info = index.campaign(campaign_app_id)
    total_amount_in_campaign = campaign_info['totalInvested']

    creator_wallet_address = get_address_from_application(campaign_app_id)

    # claim initial milestone money
    if milestone_number == 1:
        if index.check_payment_milestone(campaign_app_id) == "False":
            print("he")
            account_lst = [creator_wallet_address]
            args_list = ["Milestone", int(Today_seconds()), int(total_amount_in_campaign / 2)]
            txn = ApplicationNoOpTxn(sender, params, campaign_app_id, args_list, note="Milestone 1 money, claimed", accounts=account_lst)

            txngrp = [{'txn': encoding.msgpack_encode(txn)}]
            return txngrp

        else:
            txngrp = {"initial_payment_claimed": "TRUE"}
            return txngrp

    # submitting the milestone 1 report for Reward Campaign
    elif index.campaign_type(campaign_app_id) == "Reward" and milestone_number == 2:

        if index.check_payment_milestone(campaign_app_id) == "True":

            account_lst = [creator_wallet_address]
            args_list_3 = ["End Reward Milestone", int(Today_seconds())]
            asset_list = [index.nft_in_campaign(campaign_app_id)]

            params_txn = client.suggested_params()
            params_txn.fee = 3000
            params_txn.flat_fee = True

            # if the admin hit to approve milestone for the first time
            if approve_milestone_again == 0:

                # check the nft amount remaining in the campaign
                nft_amt_remaining = index.nft_amt_in_campaign(campaign_app_id)

            # if the admin approves the milestone even if NFT is left in the campaign
            else:

                # hard code the nft amount remaining to zero to proceed with the transaction
                nft_amt_remaining = 0

            # If there is no nft in the campaign then admin will get the transaction
            if nft_amt_remaining == 0:

                # transaction object to return
                txn = ApplicationNoOpTxn(sender, params_txn, campaign_app_id, args_list_3, accounts=account_lst, note="Milestone 2 money, claimed", foreign_assets=asset_list)
                txngrp = [{'txn': encoding.msgpack_encode(txn)}]
                return txngrp

            # if there is still an NFT in the campaign admin will not get the transaction
            elif nft_amt_remaining > 0:
                return {'message': f"NFT has not been claimed yet by the investors, NFT amount remaining to claim: {nft_amt_remaining}"}

        else:
            txngrp = {"Milestone Status": "Milestone 1 money has not been claimed yet"}
            return txngrp

    # submitting the milestone 1 report for Donation campaign
    elif index.campaign_type(campaign_app_id) == "Donation" and milestone_number == 2:

        if index.check_payment_milestone(campaign_app_id) == "True":

            account_lst = [creator_wallet_address]
            args_list_3 = ["last_milestone", int(Today_seconds())]

            txn = ApplicationNoOpTxn(sender, params, campaign_app_id, args_list_3, accounts=account_lst, note="Milestone 2 money, claimed")

            txngrp = [{'txn': encoding.msgpack_encode(txn)}]
            return txngrp

        else:
            txngrp = {"Milestone Status": "Milestone 1 money has not been claimed yet"}
            return txngrp

    # submitting the milestone 2 report
    elif milestone_number == 3:
        if index.check_payment_milestone_2(campaign_app_id) == "True":

            print(f"Calling {milestone_app_id}...")

            # get node suggested parameters
            params_txn_1 = client.suggested_params()
            params_txn_1.fee = 1000
            params_txn_1.flat_fee = True

            arg = ['3rd Milestone', int(Today_seconds())]

            txn = ApplicationNoOpTxn(sender, params_txn_1, campaign_app_id, app_args=arg, note="approve")
            txngrp = [{'txn': encoding.msgpack_encode(txn)}]
            return txngrp

        else:
            txngrp = {"Milestone Status": "Milestone 2 has not been approved yet"}
            return txngrp
    else:
        return "Wrong input"


def reject_milestones(client, sender, milestone_app_id, milestone_no, campaign_app_id, note):

    # normal reject transaction
    if milestone_no == "2":

        # get node suggested parameters
        params = client.suggested_params()
        arg = ['no_check']

        txn = ApplicationNoOpTxn(sender, params, milestone_app_id, app_args=arg, note=note)
        txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    # transaction to give the investors half of their donation back
    elif milestone_no == "1":

        # get the list of the investors and the number of investors
        investors_list = index.list_investors(campaign_app_id)
        total_investors = len(investors_list)

        # define the arguments for the transactions
        arg = ['return payment to investors, milestone rejected', int(Today_seconds()), int(total_investors)]
        investors_wallet_address_list = []

        # get node parameters
        params = client.suggested_params()
        params.fee = int(1000 * total_investors)

        # get the wallet address and the invested amount from the list
        # investments are in microAlgo format
        for investor, investment in investors_list:
            investor_wallet_address = get_address_from_application(investor)
            investors_wallet_address_list.append(investor_wallet_address)
            arg.append(int(investment/2))

        # create the transaction object
        txn = ApplicationNoOpTxn(sender, params, campaign_app_id, app_args=arg, accounts=investors_wallet_address_list, note=note)
        txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    else:
        txngrp = {'message': "Wrong milestone number"}

    return txngrp


# Group transaction: (Campaign app call and Burn Asset)
# *******************************************
def call_asset_destroy(client, asset_id, campaignID):

    # define address from private key of creator
    creator_account = get_address_from_application(campaignID)

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

    # define updated arguments
    campaign = ["update_details", bytes(title, 'utf8'), bytes(category, 'utf8'),
                int(end_time), bytes(fund_category, 'utf8'),
                int(fund_limit * 1_000_000), bytes(country, 'utf8')]

    # get node suggested parameters
    params = client.suggested_params()

    # update campaign transaction
    txn_1 = ApplicationNoOpTxn(sender, params, app_id, campaign)

    # update milestones transactions
    milestone_1 = ["update_details", bytes(milestones_title[0], 'utf-8'), int(milestone_number[0]), int(milestone_end_time[0])]
    txn_2 = ApplicationNoOpTxn(sender, params, int(milestone_id[0]), milestone_1)

    milestone_2 = ["update_details", bytes(milestones_title[1], 'utf-8'), int(milestone_number[1]), int(milestone_end_time[1])]
    txn_3 = ApplicationNoOpTxn(sender, params, int(milestone_id[1]), milestone_2)

    # compute group id and put it into each transaction
    print("Grouping transactions...")
    group_id = transaction.calculate_group_id([txn_1, txn_2, txn_3])
    print("...computed groupId: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id
    txn_3.group = group_id

    txngrp = [{'txn': encoding.msgpack_encode(txn_1)},
              {'txn': encoding.msgpack_encode(txn_2)},
              {'txn': encoding.msgpack_encode(txn_3)}]

    return txngrp


# Reason for approving/rejecting Campaign
def approve_reject_campaign(client, public_address, campaign_id, status, ESG):

    # if campaign gets rejected ESG == 0, even if the campaign is ESG
    print(f"Approving/Rejecting {campaign_id} campaign....")
    # declaring the sender
    sender = public_address

    # get node suggested parameters
    params = client.suggested_params()

    if ESG > 1:
        app_args = ["Approve/Reject ESG Campaign", int(Today_seconds()), int(status), int(ESG)]
        txn = ApplicationNoOpTxn(sender, params, campaign_id, app_args)
    else:
        app_args = ["Approve/Reject Campaign", int(Today_seconds()), int(status)]
        txn = ApplicationNoOpTxn(sender, params, campaign_id, app_args=app_args)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# block running campaign
def block_campaign(client, wallet_address, campaign_id, milestone_app_id, note):
    print(f"Blocking {campaign_id} campaign....")

    # declaring the addresses
    sender = wallet_address
    nft_in_campaign = index.nft_in_campaign(campaign_id)

    if nft_in_campaign > 0:
        # get the list of the investors and the number of investors
        investors_list = index.list_investors(campaign_id)
        total_investors = len(investors_list)

        # get node parameters
        params = client.suggested_params()
        params.fee = int((1000 * total_investors + 1000) + 1000)
        params.flat_fee = True

        # get the campaign creator address
        campaign_creator_address = get_address_from_application(campaign_id)

        # define the arguments to be passed
        app_args = ["Block Reward Campaign", int(total_investors)]
        account_list = [campaign_creator_address]
        asset_list = [nft_in_campaign]

        # get the wallet address and the invested amount from the list
        # investments are in microAlgo format
        for investor, investment in investors_list:
            investor_wallet_address = get_address_from_application(investor)
            account_list.append(investor_wallet_address)
            app_args.append(int(investment))

        # create unsigned transaction
        txn_1 = ApplicationNoOpTxn(sender, params, campaign_id, app_args, note=note, accounts=account_list, foreign_assets=asset_list)

    else:
        # get the list of the investors and the number of investors
        investors_list = index.list_investors(campaign_id)
        total_investors = len(investors_list)

        # define the arguments for the transactions
        arg = ['Block Campaign', int(total_investors)]
        investors_wallet_address_list = []

        # get node parameters
        params = client.suggested_params()
        params.fee = 1000 * int(total_investors) + 1000

        # get the wallet address and the invested amount from the list
        # investments are in microAlgo format
        for investments in investors_list:
            investor_wallet_address = get_address_from_application(investments['user_app_id'])
            investors_wallet_address_list.append(investor_wallet_address)
            arg.append(int(investments['invested']))

        # create the transaction object
        txn_1 = ApplicationNoOpTxn(sender, params, campaign_id, app_args=arg, accounts=investors_wallet_address_list, note=note)

    params_txn = client.suggested_params()

    # delete campaign: Transaction 2
    txn_2 = ApplicationDeleteTxn(sender, params_txn, campaign_id, app_args=["Block/Delete Campaign"])

    # delete milestones: transaction 3,4
    txn_3 = ApplicationDeleteTxn(sender, params_txn, int(milestone_app_id[0]))

    txn_4 = ApplicationDeleteTxn(sender, params_txn, int(milestone_app_id[1]))

    print("Grouping transactions...")
    # compute group id and put it into each transaction
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


# Reason for rejecting reward Campaign
def reject_reward_campaign(client, public_address, campaign_id, reason):

    print(f"Blocking/rejecting {campaign_id} campaign....")

    # declaring the addresses
    sender = public_address
    campaign_creator_address = get_address_from_application(campaign_id)

    # get node suggested parameters
    params = client.suggested_params()
    params.fee = 2000
    params.flat_fee = True

    # find the asset in the campaign
    asset_in_campaign = index.nft_in_campaign(campaign_id)

    # define the arguments to be passed
    app_args = ["Reject Reward Campaign"]
    accounts_list = [campaign_creator_address]
    asset_list = [asset_in_campaign]

    # create unsigned transaction
    txn = ApplicationNoOpTxn(sender, params, campaign_id, app_args, note=reason, accounts=accounts_list, foreign_assets=asset_list)

    txngrp = [{'txn': encoding.msgpack_encode(txn)}]

    return txngrp


# delete campaign and transfer nft to creator
def nft_delete(client, campaign_id, asset_id, milestone_app_id):

    print(f"Deleting {campaign_id} Campaign, {milestone_app_id} milestones and transferring {asset_id} NFT....")

    # define address from private key of creator
    sender = get_address_from_application(campaign_id)

    # set suggested params
    params = client.suggested_params()

    # set params for transaction 1
    params_txn1 = client.suggested_params()
    params_txn1.fee = 2000
    params_txn1.flat_fee = True

    # define arguments
    args_list = ["Transfer NFT to Creator"]
    asset_list = [asset_id]

    # define txn
    txn_1 = ApplicationNoOpTxn(sender=sender, sp=params_txn1, index=campaign_id, app_args=args_list, foreign_assets=asset_list)

    # delete campaign: Transaction 2
    txn_2 = ApplicationDeleteTxn(sender, params, campaign_id, app_args=['Block/Delete Campaign'])

    # delete milestones: transaction 3,4
    txn_3 = ApplicationDeleteTxn(sender, params, int(milestone_app_id[0]))
    txn_4 = ApplicationDeleteTxn(sender, params, int(milestone_app_id[1]))

    print("Grouping transactions...")
    # compute group id and put it into each transaction
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
