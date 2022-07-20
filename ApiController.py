from flask import Flask, request, jsonify
from flask_cors import CORS

import transactions.indexer
from utilities import check, CommonFunctions
from transactions import admin, creator_investor, create_update_account, indexer
from API import connection

app = Flask(__name__)

CORS(app)
cors = CORS(app, resources={
    r"/*": {
        "origin": "*"
    }
})

# Setting up connection with algorand client
algod_client = connection.algo_conn()


# Create unique id for respective accounts created.
@app.route('/create_account', methods=["POST"])
def create_account():
    # Get details of the user
    user_details = request.get_json()
    address = user_details['wallet_address']
    name = user_details['name']
    usertype = user_details['user_type']
    email = user_details['email']

    # check details of the user
    username = check.check_name(name)
    user_type = check.check_user(usertype)
    email_id = check.check_email(email)
    if username == "Approved" and user_type == "Approved" and email_id == "Approved":
        try:
            if CommonFunctions.check_balance(address, 1000):
                # give the user id for the user
                try:
                    usertxn = create_update_account.create_app(algod_client, address, name, usertype, email)
                    return jsonify(usertxn), 200
                except Exception as error:
                    return str(error), 500
            else:
                return "For Account Creation, Minimum Balance should be 1000 microAlgos", 400
        except Exception as wallet_error:
            return f"Check Wallet Address, Error: {wallet_error}", 400
    else:
        lst_error = {"Name": username, "User Type": user_type, "Email": email_id}
        return jsonify(lst_error), 400


# create unique id for admin user
@app.route('/create_admin_account', methods=['POST'])
def create_admin_account():
    # Get details of the admin
    user_details = request.get_json()
    name = user_details['name']
    usertype = user_details['user_type']
    email = user_details['email']

    # check details of the admin
    username = check.check_name(name)
    user_type = check.check_admin(usertype)
    email_id = check.check_email(email)
    if username == "Approved" and user_type == "Approved" and email_id == "Approved":
        # give the admin id for the admin
        admintxn = admin.create_admin_account(algod_client, name, usertype, email)
        return jsonify(admintxn)
    else:
        lst_error = {"Name": username, "User Type": user_type, "Email": email_id}
        return jsonify(lst_error)


# Jwt: authentic tokens

# Updating user details
@app.route('/update_account', methods=['POST'])
def update_user():
    # Get details of the user
    user_details = request.get_json()
    user_id = user_details['user_app_id']
    name = user_details['name']

    # check details of the user
    username = check.check_name(name)
    address = CommonFunctions.get_address_from_application(user_id)
    if username == "Approved":
        try:
            if CommonFunctions.check_balance(address, 1000):
                try:
                    # give the user id for the user
                    update_user_txn = create_update_account.update_user(algod_client, user_id,
                                                                        name)
                    return jsonify(update_user_txn), 200
                except Exception as error:
                    return str(error), 500
            else:
                return "For updating account information, Minimum Balance should be 1000 microAlgos", 400
        except Exception as wallet_error:
            return f"Check Wallet Address, Error: {wallet_error}", 400
    else:
        lst_error = {"Name": username}
        return jsonify(lst_error), 400


# updating admin
@app.route('/update_admin', methods=['POST'])
def update_admin():
    # Get details of the admin
    user_details = request.get_json()
    address = user_details['admin_wallet_address']
    admin_id = user_details['admin_app_id']
    name = user_details['name']
    usertype = user_details['user_type']
    email = user_details['email']

    # check details of the user
    username = check.check_username(name)
    user_type = check.check_admin(usertype)
    email_id = check.check_email(email)
    if username == "Approved" and user_type == "Approved" and email_id == "Approved":
        try:
            if CommonFunctions.check_balance(address, 1000):
                try:
                    # give the admin id for the user
                    update_admin_txn = admin.update_admin(algod_client, address, admin_id,
                                                          name, usertype, email)
                    return jsonify(update_admin_txn), 200
                except Exception as error:
                    return str(error), 500
            else:
                return "For updating account information, Minimum Balance should be 1000 microAlgos"
        except Exception as wallet_error:
            return f"Check Wallet Address, Error: {wallet_error}", 400
    else:
        lst_error = {"Name": username, "User Type": user_type, "Email": email_id}
        return jsonify(lst_error), 400


# delete account
@app.route('/delete_user', methods=['POST'])
def delete_user():
    # Get the user Details
    user_delete = request.get_json()
    user_id = user_delete['user_app_id']
    address = CommonFunctions.get_address_from_application(user_id)
    try:
        if CommonFunctions.check_balance(address, 1000):
            try:
                # delete the user by passing the params
                deleted_id_txn = create_update_account.delete_user(algod_client, user_id)
                return jsonify(deleted_id_txn), 200
            except Exception as error:
                return str(error), 500
        else:
            return "To delete account, Minimum Balance should be 1000 microAlgos", 400
    except Exception as wallet_error:
        return f"Check Wallet Address, Error: {wallet_error}", 400


# Creating a Campaign id for each campaign created by accounts.
@app.route('/create_campaign', methods=["POST"])
def create_campaign():
    # get details of the campaign to create
    campaign_details = request.get_json()
    address = campaign_details['creator_wallet_address']

    # campaign details
    title = campaign_details['title']
    category = campaign_details['category']
    end_time = campaign_details['end_time']
    fund_category = campaign_details['fund_category']
    fund_limit = campaign_details['fund_limit']
    reward_type = campaign_details['reward_type']
    country = campaign_details['country']
    milestone = campaign_details['milestone']

    # make the list from the dictionary
    milestone_title_lst = (milestone['milestone_title']['1'], milestone['milestone_title']['2'])
    milestone_list = (milestone['milestone_number']['1'], milestone['milestone_number']['2'])
    end_time_lst = (milestone['end_time_milestone']['1'], milestone['end_time_milestone']['2'])

    try:
        if CommonFunctions.check_balance(address, 4000):
            try:
                # pass the campaign details to the algorand
                campaignID_txn = creator_investor.create_campaign_app(algod_client, address, title,
                                                                      category, end_time, fund_category, fund_limit,
                                                                      reward_type, country, milestone_title_lst,
                                                                      milestone_list, end_time_lst)
                return jsonify(campaignID_txn), 200
            except Exception as error:
                return str(error), 500
        else:
            return "To create campaign, Minimum Balance should be 4000 microAlgos", 400
    except Exception as wallet_error:
        return f"Check Wallet Address, Error: {wallet_error}", 400


# update the existing campaign
@app.route('/update_campaign', methods=['POST'])
def update_campaign_details():
    # get details of the campaign to update
    campaign_details = request.get_json()
    address = campaign_details['creator_wallet_address']
    campaignID = campaign_details['campaign_app_id']
    title = campaign_details['title']
    category = campaign_details['category']
    end_time = campaign_details['end_time']
    fund_category = campaign_details['fund_category']
    fund_limit = campaign_details['fund_limit']
    country = campaign_details['country']
    milestone = campaign_details['milestone']

    # make the list from the dictionary
    milestone_app_id_lst = (milestone['milestone_app_id']['1'], milestone['milestone_app_id']['2'])
    milestone_title_lst = (milestone['milestone_title']['1'], milestone['milestone_title']['2'])
    milestone_list = (milestone['milestone_number']['1'], milestone['milestone_number']['2'])
    end_time_lst = (milestone['end_time_milestone']['1'], milestone['end_time_milestone']['2'])

    try:
        if CommonFunctions.check_balance(address, 1000):
            try:
                # pass the campaign details to the algorand
                update_campaign_txn = creator_investor.update_campaign(algod_client, address, campaignID, title,
                                                                       category, end_time, fund_category, fund_limit,
                                                                       country, milestone_app_id_lst, milestone_title_lst,
                                                                       milestone_list, end_time_lst)
                return jsonify(update_campaign_txn), 200
            except Exception as error:
                return str(error), 500
        else:
            return "To update campaign, Minimum Balance should be 1000 microAlgos", 400
    except Exception as wallet_error:
        return f"Check Wallet Address, Error: {wallet_error}", 400


# Block/Reject/Approve Campaign
@app.route('/reject_approve_campaign', methods=["POST"])
def reject_campaign():
    # Get Details
    reject_campaign_details = request.get_json()
    address = reject_campaign_details['admin_wallet_address']
    campaignID = reject_campaign_details['campaign_app_id']
    reason = reject_campaign_details['note']

    try:
        if CommonFunctions.check_balance(address, 1000):
            try:

                # transaction for approving donation/reward campaign and rejecting donation campaign
                if transactions.indexer.campaign_type(campaignID) == "Donation" or reason == 'approve':
                    reject_campaign_id_txn = creator_investor.approve_reject_campaign(algod_client, address, campaignID, reason)
                    return jsonify(reject_campaign_id_txn), 200

                # transaction for rejecting reward campaign
                if transactions.indexer.campaign_type(campaignID) == "Reward" and reason != 'approve':
                    reject_campaign_id_txn = creator_investor.reject_reward_campaign(algod_client, address, campaignID, reason)
                    return jsonify(reject_campaign_id_txn), 200

            except Exception as error:
                return str(error), 500
        else:
            return "To Approve campaign, Minimum Balance should be 1000 microAlgos", 400
    except Exception as wallet_error:
        return f"Check Wallet Address, Error: {wallet_error}", 400


# delete campaign and unfreeze nft linked with the campaign
@app.route('/delete_campaign', methods=['POST'])
def delete_campaign():
    # Get the user Details
    user_delete = request.get_json()
    campaign_app_id = int(user_delete['campaign_app_id'])
    nft_id = int(user_delete['nft_id'])
    milestone_app_id = user_delete['milestone_app_id']
    address = CommonFunctions.get_address_from_application(campaign_app_id)

    # creating the list of milestone app id
    milestones_lst = (milestone_app_id['1'], milestone_app_id['2'])

    # delete the user by passing the params
    if nft_id == 0 or nft_id == 0:
        try:
            if CommonFunctions.check_balance(address, 4000):
                try:
                    delete_campaign_txn = create_update_account.campaign_milestones(algod_client, campaign_app_id,
                                                                                    milestones_lst)
                    return jsonify(delete_campaign_txn), 200
                except Exception as error:
                    return str(error), 500
            else:
                return "To delete the campaign, Minimum Balance should be 4000 microAlgos", 400
        except Exception as wallet_error:
            return f"Check Wallet Address, Error: {wallet_error}", 400
    else:
        try:
            if CommonFunctions.check_balance(address, 5000):
                try:
                    deleted_campaign_id_txn = creator_investor.nft_delete(algod_client, campaign_app_id, nft_id,
                                                                          milestones_lst)
                    return jsonify(deleted_campaign_id_txn), 200
                except Exception as error:
                    return str(error), 500
            else:
                return f"To delete the campaign, milestones and unfreeze {nft_id} NFT," \
                       "Minimum Balance should be 5000 microAlgos", 400
        except Exception as wallet_error:
            return f"Check Wallet Address, Error: {wallet_error}", 400


# start the milestone
@app.route('/start_milestone', methods=['POST'])
def init_milestone():
    # get the details
    milestone_details = request.get_json()
    campaign_app_id = milestone_details['campaign_app_id']
    milestone_app_id = milestone_details['milestone_app_id']
    milestone_title = milestone_details['milestone_title']
    milestone_no = milestone_details['milestone_number']

    milestone_txn = creator_investor.start_milestones(algod_client, campaign_app_id, milestone_app_id, milestone_title,
                                                      milestone_no)
    return jsonify(milestone_txn)


# Group Transaction: (Call user app and mint NFT)
@app.route('/create_asset', methods=["POST"])
def mint_nft():
    # get the details of the campaign to mint asset
    mint_asset = request.get_json()
    app_id = mint_asset['app_id']
    name = mint_asset['user_name']
    usertype = mint_asset['user_type']
    unit_name = mint_asset['unit_name']
    asset_name = mint_asset['asset_name']
    meta_hash = mint_asset['image_hash']
    NFT_price = mint_asset['NFT_price']
    # meta = mint_asset['hash']
    # b_meta = bytes(meta, 'utf-8')

    address = CommonFunctions.get_address_from_application(app_id)

    try:
        if CommonFunctions.check_balance(address, 1000+NFT_price):
            try:
                # pass the details to algorand to mint asset
                asset_txn = admin.admin_asset(algod_client, name, usertype, app_id,
                                              unit_name, asset_name, meta_hash, NFT_price)

                return jsonify(asset_txn), 200
            except Exception as error:
                return str(error), 500
        else:
            return f"To Mint NFT, Minimum Balance should be 1000+{NFT_price} microAlgos", 400
    except Exception as wallet_error:
        return f"Check Wallet Address, Error: {wallet_error}", 400


# Opt-in to NFT
# ***NO SCREEN***
@app.route('/optin_nft', methods=["POST"])
def asset_optin():
    # get the details for optin the NFT
    transfer_details = request.get_json()
    address = transfer_details['wallet_address']
    asset_id = transfer_details['NFT_asset_id']

    try:
        if CommonFunctions.check_balance(address, 1000):
            try:
                txn_details = creator_investor.opt_in(algod_client, address, asset_id)
                return jsonify(txn_details), 200
            except Exception as error:
                return str(error), 500
        else:
            return f"To Opt-in in {asset_id} NFT, Minimum Balance should be 1000 microAlgos", 400
    except Exception as wallet_error:
        return f"Check Wallet Address, Error: {wallet_error}", 400


# Transfer NFT from admin to campaign creator
@app.route('/transfer_asset', methods=["POST"])
def transfer_nft():
    # get the details for transferring the NFT
    transfer_details = request.get_json()
    asset_id = transfer_details['NFT_asset_id']
    nft_amount = transfer_details['nft_amount']
    admin_address = transfer_details['admin_wallet_address']
    creator_address = transfer_details['creator_wallet_address']

    try:
        if CommonFunctions.check_balance(admin_address, 1000):
            try:
                # send the details to transfer NFT
                txn_details = creator_investor.admin_creator(algod_client, asset_id,
                                                             nft_amount, admin_address, creator_address)
                return jsonify(txn_details), 200
            except Exception as error:
                return str(error), 500
        else:
            return f"To transfer {asset_id} NFT, Minimum Balance should be 1000 microAlgos", 400
    except Exception as wallet_error:
        return f"Check Wallet Address, Error: {wallet_error}", 400


# sending NFT to Campaign
@app.route('/campaign_nft', methods=['POST'])
def campaign_nft():
    # get the details
    nft = request.get_json()
    asset_id = nft['NFT_asset_id']
    campaign_id = nft['campaign_app_id']
    address = CommonFunctions.get_address_from_application(campaign_id)

    try:
        if CommonFunctions.check_balance(address, 3000):
            try:
                # send the details
                txn_id = creator_investor.nft_to_campaign(algod_client, asset_id, campaign_id)
                return jsonify(txn_id), 200
            except Exception as error:
                return str(error), 500
        else:
            return "To assign NFT to a campaign, Minimum Balance should be 3000 microAlgos", 400
    except Exception as wallet_error:
        return f"Check Wallet Address, Error: {wallet_error}", 400


# Transfer NFT from Campaign Creator to Investor
@app.route('/investor_nft_claimed', methods=["POST"])
def clamming_nft():
    # getting the transaction details
    transfer_details = request.get_json()
    user_app_id = transfer_details['user_app_id']
    asset_id = transfer_details['nft_asset_id']
    campaign_app_id = transfer_details['campaign_app_id']

    investor_address = CommonFunctions.get_address_from_application(user_app_id)

    try:
        if CommonFunctions.check_balance(investor_address, 3000):
            try:
                # send the details for transaction to occur
                txn_details = creator_investor.claim_nft(algod_client, user_app_id,
                                                         asset_id, campaign_app_id)
                return jsonify(txn_details), 200
            except Exception as error:
                return str(error), 500
        else:
            return f"To transfer {asset_id} NFT, Minimum Balance should be 3000 microAlgos", 400
    except Exception as wallet_error:
        return f"Check Wallet Address, Error: {wallet_error}", 400


# destroy asset, Group transaction: (campaign call app and destroy asset)
@app.route('/burn_asset', methods=["POST"])
def burnAsset():
    asset_details = request.get_json()
    asset_id = asset_details['NFT_asset_id']
    campaignID = asset_details['campaign_app_id']
    burnAssetTxn = creator_investor.call_asset_destroy(algod_client,
                                                       asset_id, campaignID)
    txn_json = {"transaction_id": burnAssetTxn}
    return jsonify(txn_json), 200


# Investor Participating in Campaign by investing.
@app.route('/participating', methods=["POST"])
def participation():
    # get the details of investor participation's
    participation_details = request.get_json()
    campaignID = participation_details['campaign_app_id']
    investment = float(participation_details['amount'])
    investor_account = participation_details['investor_wallet_address']
    meta_data = str(participation_details['metadata'])

    participationID=creator_investor.update_call_app(algod_client, campaignID,
                                                     investment, investor_account, meta_data)
    return jsonify(participationID), 200


# admin approves the milestone and investment get transfer to creator
@app.route('/approve_milestone', methods=["POST"])
def approve_milestone():
    # get the details from the user
    investment_details = request.get_json()
    campaign_app_id = investment_details['campaign_app_id']
    milestone_no = investment_details['milestone_number']
    admin_wallet_address = investment_details['admin_wallet_address']
    milestone_app_id = investment_details['milestone_app_id']

    # pass the details to the algorand to run the transaction
    txn_details = creator_investor.pull_investment(algod_client, admin_wallet_address, campaign_app_id, milestone_no,
                                                   milestone_app_id)
    return jsonify(txn_details)


# admin approves the milestone and investment get transfer to creator
@app.route('/reject_milestone', methods=["POST"])
def reject_milestone():
    # get the details from the user
    investment_details = request.get_json()
    admin_wallet_address = investment_details['admin_wallet_address']
    milestone_app_id = investment_details['milestone_app_id']
    note = investment_details['note']

    # pass the details to the algorand to run the transaction
    txn_details = creator_investor.reject_milestones(algod_client, admin_wallet_address, milestone_app_id, note)
    return jsonify(txn_details)


# admin approves the milestone and investment get transfer to creator
@app.route('/claim_milestone_1', methods=["POST"])
def milestone1_start():
    # get the details from the user
    investment_details = request.get_json()
    campaign_app_id = investment_details['campaign_app_id']
    milestone_no = 1
    creator_wallet_address = investment_details['creator_wallet_address']

    # pass the details to the algorand to run the transaction
    txn_details = creator_investor.pull_investment(algod_client, creator_wallet_address, campaign_app_id, milestone_no)

    if txn_details == {"initial_payment_claimed": "TRUE"}:
        return jsonify(txn_details), 400
    else:
        return jsonify(txn_details), 200


# check milestone 1
@app.route('/check_initial_payment/<int:campaign_app_id>')
def check_milestone(campaign_app_id):
    # pass the details
    check_info = indexer.check_payment_milestone_again(campaign_app_id)
    return jsonify(check_info), 200


# get the list of the total investors in campaign
@app.route('/investors_list_campaign/<int:campaign_id>')
def investors_list_in_campaign(campaign_id):

    # pass the details
    try:
        check_nft_wallet = indexer.list_investors(campaign_id)
        return jsonify(check_nft_wallet), 200
    except Exception as error:
        return str(error), 400


# check if the user has claimed the NFT
@app.route('/investor_nft_claimed/<int:campaign_app_id>/<int:user_app_id>')
def check_nft(campaign_app_id, user_app_id):

    # pass the details
    result = indexer.check_claim_nft(user_app_id, campaign_app_id)
    print(result)

    if len(result) == 1:
        claim_info = [result[0]]
    else:
        claim_info = [result[0], result[1]]

    return jsonify(claim_info), 200


# NFT in Campaign
@app.route('/nft_in_campaign/<int:campaign_app_id>')
def nft_in_campaign(campaign_app_id):

    # pass the details
    nft_campaign = indexer.nft_in_wallet(campaign_app_id)
    return jsonify(nft_campaign)


# Get total NFT
@app.route('/total_nft/<int:app_id>')
def totalNFT(app_id):
    try:
        assets = indexer.assets_in_wallet(app_id)

        return jsonify(assets), 200
    except Exception as Error:
        print(f"Check User App ID! Error: {Error}")


# Get total NFT
@app.route('/nft_info/<int:nft_id>')
def asset_info(nft_id):
    try:
        assets = indexer.asset_details(nft_id)
        return jsonify(assets), 200
    except Exception as Error:
        print(f"Check Asset ID! Error: {Error}")


# Get the details of the campaign
@app.route('/campaign_details/<int:campaign_id>')
def campaign_info(campaign_id):
    info = indexer.campaign(campaign_id)
    return jsonify(info)


# running the API
if __name__ == "__main__":
    app.run(debug=True, port=3000)
