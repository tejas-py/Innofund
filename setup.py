from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
from os import path, stat
from utilities import check, CommonFunctions
from transactions import admin, creator_investor, create_update_account, institutional_donor, grant_creator, grant_applicant, index
from API import connection

# defining the flask app and setting up cors
app = Flask(__name__)
cors = CORS(app, resources={
    r"/*": {"origin": "*"}
})

# Setting up connection with algorand client
algod_client = connection.algo_conn()


# home page
@app.route('/')
def home_page():
    return redirect("https://www.cashdillo.com", code=302)


# favicon
@app.route('/favicon.ico')
def favicon():
    favicon_image = send_from_directory(path.join(app.root_path, 'static'),
                                        'favicon.ico')
    return favicon_image, 200


# 404 error handling
@app.errorhandler(404)
def page_not_found(e):
    return f"<title>Page Not Found</title><h1>404 Not Found</h1><p>{e}</p>", 404


# Create unique id for accounts(Donors and Creators)
@app.route('/create_account', methods=["POST"])
def create_account():

    try:
        # Get details of the user
        user_details = request.get_json()
        address = user_details['wallet_address']
        usertype = user_details['user_type']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    # check details of the user
    user_type = check.check_user(usertype)
    if user_type == "Approved":
        try:
            if CommonFunctions.check_balance(address, 1000):
                # give the user id for the user
                try:
                    usertxn = create_update_account.create_app(algod_client, address, usertype)
                    return jsonify(usertxn), 200
                except Exception as error:
                    return jsonify({"message": str(error)}), 500
            else:
                error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
                return jsonify(error_msg), 400
        except Exception as wallet_error:
            error_msg = {"message": "Wallet Error!" + str(wallet_error)}
            return jsonify(error_msg), 400
    else:
        error_msg = {"message": "wrong user type"}
        return jsonify(error_msg), 400


# create unique id for admin user
@app.route('/create_admin_account', methods=['POST'])
def create_admin_account():

    # give the admin id for the admin
    admin_user_id = admin.create_admin_account(algod_client)
    json_return = {"Admin App Id": admin_user_id}
    return jsonify(json_return)


# delete account
@app.route('/delete_user', methods=['POST'])
def delete_user():
    try:
        # Get the user Details
        user_delete = request.get_json()
        user_id = int(user_delete['user_app_id'])
        address = CommonFunctions.get_address_from_application(user_id)
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(address, 1000):
            try:
                # delete the user by passing the params
                deleted_id_txn = create_update_account.delete_user(algod_client, user_id)
                return jsonify(deleted_id_txn), 200
            except Exception as error:
                return jsonify({"message": str(error)}), 500
        else:
            return jsonify({"message": "To delete account, Minimum Balance should be 1000 microAlgos"}), 400
    except Exception as wallet_error:
        return jsonify({"message": f"Check Wallet Address, Error: {wallet_error}"}), 400


# Creating a Campaign id for each campaign created by accounts.
@app.route('/create_campaign', methods=["POST"])
def create_campaign():
    try:
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
        ESG = campaign_details['ESG']
        milestone = campaign_details['milestone']

        # make the list from the dictionary
        milestone_title_lst = (milestone['milestone_title']['1'], milestone['milestone_title']['2'])
        milestone_list = (milestone['milestone_number']['1'], milestone['milestone_number']['2'])
        end_time_lst = (milestone['end_time_milestone']['1'], milestone['end_time_milestone']['2'])
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(address, 3000):
            try:
                # pass the campaign details to the algorand
                campaignID_txn = creator_investor.create_campaign_app(algod_client, address, title,
                                                                      category, end_time, fund_category, fund_limit,
                                                                      reward_type, country, ESG, milestone_title_lst,
                                                                      milestone_list, end_time_lst)
                print(campaignID_txn)
                return jsonify(campaignID_txn), 200
            except Exception as error:
                error_msg = {"message": str(error)}
                return jsonify(error_msg), 500
        else:
            error_msg = {"message": "To create campaign, Minimum Balance should be 3000 microAlgos"}
            return jsonify(error_msg), 400
    except Exception as wallet_error:
        error_msg = {"message": str(wallet_error)}
        return jsonify(error_msg), 400


# update the existing campaign
@app.route('/update_campaign', methods=['POST'])
def update_campaign_details():
    try:
        # get details of the campaign to update
        campaign_details = request.get_json()
        address = campaign_details['creator_wallet_address']
        campaignID = int(campaign_details['campaign_app_id'])
        title = campaign_details['title']
        category = campaign_details['category']
        end_time = campaign_details['end_time']
        fund_category = campaign_details['fund_category']
        fund_limit = int(campaign_details['fund_limit'])
        country = campaign_details['country']
        milestone = campaign_details['milestone']

        # make the list from the dictionary
        milestone_app_id_lst = (milestone['milestone_app_id']['1'], milestone['milestone_app_id']['2'])
        milestone_title_lst = (milestone['milestone_title']['1'], milestone['milestone_title']['2'])
        milestone_list = (milestone['milestone_number']['1'], milestone['milestone_number']['2'])
        end_time_lst = (milestone['end_time_milestone']['1'], milestone['end_time_milestone']['2'])
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(address, 3000):
            try:
                # pass the campaign details to the algorand
                update_campaign_txn = creator_investor.update_campaign(algod_client, address, campaignID, title,
                                                                       category, end_time, fund_category, fund_limit,
                                                                       country, milestone_app_id_lst, milestone_title_lst,
                                                                       milestone_list, end_time_lst)
                return jsonify(update_campaign_txn), 200
            except Exception as error:
                error_msg = {"message": error}
                return jsonify(error_msg), 500
        else:
            error_msg = {"message": "To update campaign, Minimum Balance should be 3000 microAlgos"}
            return jsonify(error_msg), 400
    except Exception as wallet_error:
        return jsonify({"message": f"Check Wallet Address, Error: {str(wallet_error)}"}), 400


# Block/Reject/Approve Campaign
@app.route('/reject_approve_campaign', methods=["POST"])
def reject_approve_campaign():
    try:
        # Get Details
        reject_campaign_details = request.get_json()
        address = reject_campaign_details['admin_wallet_address']
        campaignID = reject_campaign_details['campaign_app_id']
        status = int(reject_campaign_details['note']) # value = 0 if rejected, value = 1 if approved
        ESG = int(reject_campaign_details['ESG'])
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(address, 1000):
            try:

                # transaction for approving donation/reward campaign and rejecting donation campaign
                if index.campaign_type(campaignID) == "Donation" or status == 1:
                    reject_campaign_id_txn = creator_investor.approve_reject_campaign(algod_client, address, campaignID, status, ESG)
                    return jsonify(reject_campaign_id_txn), 200

                # transaction for rejecting reward campaign
                if index.campaign_type(campaignID) == "Reward" and status != 1:
                    reject_campaign_id_txn = creator_investor.reject_reward_campaign(algod_client, address, campaignID, status)
                    return jsonify(reject_campaign_id_txn), 200

            except Exception as error:
                print(error)
                return jsonify({'message': str(error)}), 500
        else:
            return jsonify({'message': "To Approve campaign, Minimum Balance should be 1000 microAlgos"}), 400
    except Exception as error:
        return jsonify({'message': str(error)}), 400


# Block the running campaign
@app.route('/block_campaign', methods=["POST"])
def block_campaign():
    try:
        # get the details
        user_block = request.get_json()
        campaign_app_id = user_block['campaign_app_id']
        milestone_app_id = user_block['milestone_app_id']
        wallet_address = user_block['admin_wallet_address']
        note = "Block Running Campaign"
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(wallet_address, 4000):
            try:
                # create the transaction object
                txn = creator_investor.block_campaign(algod_client, wallet_address, campaign_app_id, milestone_app_id, note)
                return jsonify(txn), 200
            except Exception as error:
                print(error)
                return jsonify({'message': str(error)}), 400
        else:
            return jsonify({'message': "To Block campaign, Minimum Balance should be 4000 microAlgos"}), 400

    except Exception as error:
        jsonify({'message': str(error)}), 400


# delete campaign and unfreeze nft linked with the campaign
@app.route('/delete_campaign', methods=['POST'])
def delete_campaign():
    try:
        # Get the user Details
        user_delete = request.get_json()
        campaign_app_id = int(user_delete['campaign_app_id'])
        nft_id = int(user_delete['nft_id'])
        milestone_app_id = user_delete['milestone_app_id']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

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
                    return jsonify({"message": str(error)}), 500
            else:
                return jsonify({"message": "To delete the campaign, Minimum Balance should be 4000 microAlgos"}), 400
        except Exception as wallet_error:
            return jsonify({"message": f"Check Wallet Address, Error: {wallet_error}"}), 400
    else:
        try:
            if CommonFunctions.check_balance(address, 5000):
                try:
                    deleted_campaign_id_txn = creator_investor.nft_delete(algod_client, campaign_app_id, nft_id,
                                                                          milestones_lst)
                    return jsonify(deleted_campaign_id_txn), 200
                except Exception as error:
                    return jsonify({"message": str(error)}), 500
            else:
                return jsonify({"message": f"To delete the campaign, milestones and unfreeze {nft_id} NFT, Minimum Balance should be 5000 microAlgos"}), 400
        except Exception as wallet_error:
            return jsonify({"message": f"Check Wallet Address, Error: {wallet_error}"}), 400


# start the milestone
@app.route('/start_milestone', methods=['POST'])
def init_milestone():
    try:
        # get the details
        milestone_details = request.get_json()
        campaign_app_id = milestone_details['campaign_app_id']
        milestone_app_id = milestone_details['milestone_app_id']
        milestone_title = milestone_details['milestone_title']
        milestone_no = milestone_details['milestone_number']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    milestone_txn = creator_investor.start_milestones(algod_client, campaign_app_id, milestone_app_id, milestone_title,
                                                      milestone_no)
    return jsonify(milestone_txn)


# Group Transaction: (Call user app and mint NFT)
@app.route('/create_asset', methods=["POST"])
def mint_nft():
    try:
        # get the details of the campaign to mint asset
        mint_asset = request.get_json()
        app_id = mint_asset['app_id']
        usertype = mint_asset['user_type']
        unit_name = mint_asset['unit_name'].upper()
        asset_name = mint_asset['asset_name']
        meta_hash = mint_asset['image_hash']
        description = mint_asset['description']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    address = CommonFunctions.get_address_from_application(app_id)

    try:
        if CommonFunctions.check_balance(address, 1000):
            if unit_name.isalpha():
                try:
                    # pass the details to algorand to mint asset
                    asset_txn = admin.admin_asset(algod_client, usertype, app_id,
                                                  unit_name, asset_name, meta_hash, description)

                    return jsonify(asset_txn), 200
                except Exception as error:
                    return jsonify({'message': str(error)}), 500
            else:
                return jsonify({'message': "NFT Name can only in Alphabets"}), 400
        else:
            return jsonify({'message': f"To Mint NFT, Minimum Balance should be 1000 microAlgos"}), 400
    except Exception as wallet_error:
        return jsonify({'message': f"Check Wallet Address, Error: {wallet_error}"}), 400


# Transfer nft to the marketplace
@app.route('/nft_marketplace/transfer_nft_to_marketplace', methods=['POST'])
def transfer_nft_to_marketplace():
    try:
        # get the details
        transaction_details = request.get_json()
        asset_id = transaction_details['nft_id']
        admin_application_id = 107294801
        wallet_address = transaction_details['admin_wallet_address']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(wallet_address, 2000):
            # send the details to create transactions
            txn = admin.transfer_nft_to_application(algod_client, asset_id, admin_application_id, wallet_address)
            return jsonify(txn), 200
        else:
            return jsonify({'message': "Check the wallet Balance"}), 500
    except Exception as error:
        return jsonify({'message': str(error)}), 500


# Withdraw nft from marketplace
@app.route('/nft_marketplace/withdraw_nft', methods=['POST'])
def withdraw_nft():

    try:
        # get the details
        transaction_details = request.get_json()
        asset_id = transaction_details['nft_id']
        admin_application_id = 107294801
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500
    wallet_address = CommonFunctions.get_address_from_application(admin_application_id)

    try:
        if CommonFunctions.check_balance(wallet_address, 1000):
            # send the details to create transactions
            txn = admin.withdraw_nft_from_marketplace(algod_client, asset_id, admin_application_id, wallet_address)
            return jsonify(txn), 200
        else:
            return jsonify({'message': "Check the wallet Balance"}), 500
    except Exception as error:
        return jsonify({'message': str(error)}), 500


# Buy NFT for creator from marketplace
@app.route('/nft_marketplace/buy_nft', methods=['POST'])
def buy_nft():
    try:
        # get the details
        transaction_detail = request.get_json()
        asset_id = transaction_detail['nft_id']
        user_app_id = transaction_detail['user_app_id']
        nft_price = transaction_detail['nft_price']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    wallet_address = CommonFunctions.get_address_from_application(user_app_id)

    try:
        if CommonFunctions.check_balance(wallet_address, 3000):
            txn = admin.buy_nft(algod_client, asset_id, user_app_id, nft_price)
            return jsonify(txn), 200
        else:
            return jsonify({'message': 'Check Wallet balance'}), 500
    except Exception as error:
        return jsonify({'message': str(error)}), 500


# List of NFT marketplace for creators
@app.route('/nft_marketplace', methods=['GET'])
def nft_marketplace():

    admin_application_id = 107294801

    try:
        nft_list = index.assets_in_wallet(admin_application_id)
        return jsonify(nft_list), 200
    except Exception as error:
        return jsonify({'message': str(error)}), 500


# Single NFT information for marketplace
@app.route('/nft_marketplace/nft_info/<int:asset_id>', methods=['GET'])
def nft_info(asset_id):
    try:
        nft_description = index.asset_details(asset_id)
        return jsonify(nft_description), 200
    except Exception as error:
        return jsonify({'message': str(error)}), 500


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

    try:
        # get the details for transferring the NFT
        transfer_details = request.get_json()
        asset_id = transfer_details['NFT_asset_id']
        nft_amount = transfer_details['nft_amount']
        admin_address = transfer_details['admin_wallet_address']
        creator_address = transfer_details['creator_wallet_address']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

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

    try:
        # get the details
        nft = request.get_json()
        asset_id = nft['NFT_asset_id']
        campaign_id = nft['campaign_app_id']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    address = CommonFunctions.get_address_from_application(campaign_id)

    try:
        if CommonFunctions.check_balance(address, 3000):
            try:
                # send the details
                txn_id = creator_investor.nft_to_campaign(algod_client, asset_id, campaign_id)
                return jsonify(txn_id), 200
            except Exception as error:
                return jsonify({'message': str(error)}), 500
        else:
            return jsonify({'message': "To assign NFT to a campaign, Minimum Balance should be 3000 microAlgos"}), 400
    except Exception as wallet_error:
        return jsonify({'message': f"Check Wallet Address, Error: {wallet_error}"}), 400


# Transfer NFT from Campaign Creator to Investor
@app.route('/investor_nft_claimed', methods=["POST"])
def clamming_nft():

    try:
        # getting the transaction details
        transfer_details = request.get_json()
        user_app_id = transfer_details['user_app_id']
        asset_id = transfer_details['nft_asset_id']
        campaign_app_id = transfer_details['campaign_app_id']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    investor_address = CommonFunctions.get_address_from_application(user_app_id)

    try:
        if CommonFunctions.check_balance(investor_address, 3000):
            try:
                # send the details for transaction to occur
                txn_details = creator_investor.claim_nft(algod_client, user_app_id,
                                                         asset_id, campaign_app_id)
                return jsonify(txn_details), 200
            except Exception as error:
                return jsonify({'message': str(error)}), 500
        else:
            return jsonify({'message': f"To transfer {asset_id} NFT, Minimum Balance should be 3000 microAlgos"}), 400
    except Exception as wallet_error:
        return jsonify({'message': f"Check Wallet Address, Error: {wallet_error}"}), 400


# destroy asset, Group transaction: (campaign call app and destroy asset)
@app.route('/burn_asset', methods=["POST"])
def burn_asset():
    asset_details = request.get_json()
    asset_id = asset_details['NFT_asset_id']
    campaignID = asset_details['campaign_app_id']
    burnAssetTxn = creator_investor.call_asset_destroy(algod_client,
                                                       asset_id, campaignID)
    txn_json = {"transaction_id": burnAssetTxn}
    return jsonify(txn_json), 200


# Investor Participating in Campaign by investing.
@app.route('/participating', methods=["POST"])
def investing():
    try:
        # get the details of investor participation's
        participation_details = request.get_json()
        campaignID = participation_details['campaign_app_id']
        investment = float(participation_details['amount'])
        investor_account = participation_details['investor_wallet_address']
        meta_data = str(participation_details['metadata'])
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(investor_account, 2000+investment) and investment != 0:
            try:
                participationID = creator_investor.update_call_app(algod_client, campaignID,
                                                                   investment, investor_account, meta_data)
                return jsonify(participationID), 200
            except Exception as error:
                return jsonify({'message': str(error)}), 500
        else:
            return jsonify({'message': 'Wallet balance low!'}), 500
    except Exception as error:
        return jsonify({'message': f'Wallet error! {error}'}), 400


# Investment by Institutional Donors
@app.route('/multiple_investments', methods=['POST'])
def multi_investing():

    try:
        # get the details
        investment_details = request.get_json()
        # test_dict = {'investments': {123:123, 345:123}, 'fees': 4000}
        campaign_investment = investment_details['investments_details']
        address = investment_details['investor_wallet_address']
        note = str(investment_details['meta_data'])
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    # donation amount
    donation = float(campaign_investment['fee'])
    # find the total amount for investing
    for campaign_id in campaign_investment['investments']:
        investment = campaign_investment['investments'][campaign_id]
        donation += float(investment)

    try:
        if CommonFunctions.check_balance(address, int(donation*1000_000)+1000):
            try:
                # txn to sub-escrow account
                txn = institutional_donor.transfer_sub_escrow_account(algod_client, campaign_investment, address, note)

                return jsonify(txn), 200
            except Exception as error:
                return jsonify({'message': f"Internal Error! {error}"}), 500
        else:
            return jsonify({'message': 'Wallet balance low'}), 400
    except Exception as error:
        return jsonify({'message': f"Wallet error! {error}"}), 400


# Transaction from sub-escrow account to campaign account
@app.route('/transfer_to_campaign', methods=['POST'])
def sub_escrow_to_campaign():

    try:
        # get the details
        transaction_details = request.get_json()
        campaign_investment = transaction_details['investments_details']
        note = str(transaction_details['meta_data'])
        address = transaction_details['investor_wallet_address']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    # txn from sub-escrow account to escrow account
    txn_ids = []
    for campaign_app_id in campaign_investment['investments']:
        # amount to transfer to every campaign
        one_investment = campaign_investment['investments'][campaign_app_id]
        amt = float(one_investment)*10**6
        # creating transaction and getting transaction id
        try:
            txn_id = institutional_donor.escrow_campaign(algod_client, address, int(campaign_app_id), int(amt), note)
        except Exception as E:
            return jsonify({'message': str(E), 'investments_details': txn_ids}), 500
        txn_details = {"campaignAppId": int(campaign_app_id), "transactionId": txn_id}
        # appending multiple transaction id
        txn_ids.append(txn_details)
    return jsonify(txn_ids), 200


# admin approves the milestone and investment get transfer to creator
@app.route('/approve_milestone', methods=["POST"])
def approve_milestone():
    try:
        # get the details from the user
        investment_details = request.get_json()
        campaign_app_id = int(investment_details['campaign_app_id'])
        milestone_no = investment_details['milestone_number']
        admin_wallet_address = investment_details['admin_wallet_address']
        milestone_app_id = int(investment_details['milestone_number'])

        """approve_milestone_again = 0 if admin confirms the milestone and checks the NFT amount in the campaign is zero. 
        approve_milestone_again = 1 if the admin confirms to approve the milestone even if there is an NFT in 
        the campaign remaining i.e., the investor didn't claim the nft in time"""

    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(admin_wallet_address, 2000):
            try:
                # pass the details to the algorand to run the transaction
                txn_details = creator_investor.pull_investment(algod_client, admin_wallet_address, campaign_app_id,
                                                               milestone_no, milestone_app_id)

                for result in txn_details[0]:
                    if result == 'txn':
                        return jsonify(txn_details), 200
                    else:
                        return jsonify(txn_details), 400
            except Exception as error:
                return jsonify({'message': str(error)}), 500
        else:
            return jsonify({'message': "Minimum Balance should be 2000 microAlgos"}), 400
    except Exception as wallet_error:
        return jsonify({'message': f"Check Wallet Address, Error: {wallet_error}"}), 400


# admin approves the milestone and investment get transfer to creator
@app.route('/reject_milestone', methods=["POST"])
def reject_milestone():

    try:
        # get the details from the user
        investment_details = request.get_json()
        admin_wallet_address = investment_details['admin_wallet_address']
        campaign_app_id = investment_details['campaign_app_id']
        milestone_app_id = investment_details['milestone_app_id']
        milestone_number = investment_details['milestone_number']
        note = investment_details['note']
        print(milestone_number)
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(admin_wallet_address, 1000):
            try:
                # pass the details to the algorand to run the transaction
                txn_details = creator_investor.reject_milestones(algod_client, admin_wallet_address, milestone_app_id, str(milestone_number), campaign_app_id, note)

                for result in txn_details[0]:
                    if result == 'txn':
                        return jsonify(txn_details), 200
                    else:
                        return jsonify(txn_details), 400

            except Exception as error:
                return jsonify({'message': str(error)}), 500
        else:
            return jsonify({'message': "Wallet balance low!"}), 400
    except Exception as E:
        return jsonify({'message': f"Wallet error! {E}"}), 400


# admin approves the milestone and investment get transfer to creator
@app.route('/claim_milestone_1', methods=["POST"])
def milestone1_claim():

    try:
        # get the details from the user
        investment_details = request.get_json()
        campaign_app_id = investment_details['campaign_app_id']
        milestone_no = 1
        creator_wallet_address = investment_details['creator_wallet_address']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 400

    try:
        if CommonFunctions.check_balance(creator_wallet_address, 1000):
            try:
                # pass the details to the algorand to run the transaction
                txn_details = creator_investor.pull_investment(algod_client, creator_wallet_address, campaign_app_id, milestone_no)
                if txn_details == {"initial_payment_claimed": "TRUE"}:
                    return jsonify(txn_details), 400
                else:
                    return jsonify(txn_details), 200
            except Exception as error:
                jsonify({'message': str(error)}), 500
        else:
            return jsonify({'message': "Wallet balance low"}), 400
    except Exception as error:
        return jsonify({'message': f"Wallet Error! {error}"})


# check milestone 1
@app.route('/check_initial_payment/<int:campaign_app_id>')
def check_milestone(campaign_app_id):
    # pass the details
    check_info = index.check_payment_milestone_again(campaign_app_id)
    return jsonify(check_info), 200


# get the list of the total investors in campaign
@app.route('/investors_list_campaign/<int:campaign_id>')
def investors_list_in_campaign(campaign_id):

    # pass the details
    try:
        check_nft_wallet = index.list_investors(campaign_id)
        return jsonify(check_nft_wallet), 200
    except Exception as error:
        return str(error), 400


# check if the user has claimed the NFT
@app.route('/investor_nft_claimed/<int:campaign_app_id>/<int:user_app_id>')
def check_nft(campaign_app_id, user_app_id):

    # pass the details
    result = index.check_claim_nft(user_app_id, campaign_app_id)
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
    nft_campaign = index.nft_in_wallet(campaign_app_id)
    return jsonify(nft_campaign)


# Get total NFT
@app.route('/total_nft/<int:app_id>')
def total_nft(app_id):
    try:
        assets = index.assets_in_wallet(app_id)

        return jsonify(assets), 200
    except Exception as Error:
        print(f"Check User App ID! Error: {Error}")


# Get total NFT
@app.route('/nft_info/<int:nft_id>')
def asset_info(nft_id):
    try:
        assets = index.asset_details(nft_id)
        return jsonify(assets), 200
    except Exception as Error:
        print(f"Check Asset ID! Error: {Error}")


# Get the details of the campaign
@app.route('/campaign_details/<int:campaign_id>')
def campaign_info(campaign_id):
    info = index.campaign(campaign_id)
    return jsonify(info), 200


# NFT Files tp upload to IPFS
@app.route('/ipfs', methods=['POST'])
def upload_ipfs():

    # extension support
    extensions_allowed = ['jpg', 'jpeg', 'png', 'gif', 'ico', 'icon', 'webp', 'tiff', 'raw', 'jpeg2000', 'svg', 'pdf', 'jfif', # images
                          'mp4', 'mov', 'wmv', 'avi', 'avchd', 'flv', 'f4v', 'swf', 'mkv', 'mpeg2', # Videos
                          'pcm', 'wav', 'aiff', 'mp3', 'aac', 'ogg', 'wma', 'flac', 'alac'] # Audio

    # get the file and the user app id
    try:
        file_info = request.files['file']
        user_app_id = request.values['userAppId']
    except Exception as error:
        return jsonify({'message': f"Payload Error! {error}"}), 400

    # check the file extension
    file_name = file_info.filename.split('.')
    file_extension = file_name[len(file_name)-1]
    if file_extension not in extensions_allowed:
        return jsonify({'message': 'File type not supported'}), 400
    else:
        pass

    # get the extension of the file and save it on local storage
    try:
        file_location = f"/home/ubuntu/Innofund/static/nft_images/" \
                        f"{user_app_id}_{CommonFunctions.Today_seconds()}.{file_extension}"
        file_info.save(file_location)
    except Exception as error:
        return jsonify({'message': f"Directory not found, Error: {error}"}), 500

    # check the file size in MB
    file_stats = stat(file_location)
    file_size = file_stats.st_size / 1_048_576

    if file_size > 100:
        return jsonify({'message': 'File size too large'}), 400
    else:
        pass

    # upload the file to IPFS client
    try:
        api = connection.ipfs_client()
        res = api.add(file_location)
        return jsonify({'url': f"https://ipfs.io/ipfs/{res[0]['Hash']}"}), 200
    except Exception as error:
        return jsonify({'message': f"Server Not Connected, IPFS Down, Error: {error}"}), 500


'''
========================================================================================================================
                            Grant Module: Grant-Creator, Grant-Manager, Grant-Applicant
========================================================================================================================
'''


# Grant Creator Account
@app.route('/grant_creator/create_account', methods=['POST'])
def grant_creator_account():
    try:
        # Get details of the user
        creator_details = request.get_json()
        address = creator_details['wallet_address']
        usertype = creator_details['user_type']
        organisation_name = creator_details['organisation_name']
        organisation_role = creator_details['organisation_role']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    # check details of the user
    user_type = check.check_user(usertype)
    if user_type == "Approved":
        try:
            if CommonFunctions.check_balance(address, 1000):
                # give the user id for the user
                try:
                    usertxn = grant_creator.grant_admin_app(algod_client, address, organisation_name, organisation_role, usertype)
                    return jsonify(usertxn), 200
                except Exception as error:
                    return jsonify({"message": str(error)}), 500
            else:
                error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
                return jsonify(error_msg), 400
        except Exception as wallet_error:
            error_msg = {"message": "Wallet Error!" + str(wallet_error)}
            return jsonify(error_msg), 400
    else:
        error_msg = {"message": "wrong user type"}
        return jsonify(error_msg), 400


# Grant Applicant Account
@app.route('/grant_applicant/create_account', methods=["POST"])
def grant_applicant_account():

    try:
        # Get details of the user
        user_details = request.get_json()
        address = user_details['wallet_address']
        usertype = user_details['user_type']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    # check details of the user
    user_type = check.check_user(usertype)
    if user_type == "Approved":
        try:
            if CommonFunctions.check_balance(address, 1000):
                # give the user id for the user
                try:
                    usertxn = grant_applicant.grant_applicant_app(algod_client, address, usertype)
                    return jsonify(usertxn), 200
                except Exception as error:
                    return jsonify({"message": str(error)}), 500
            else:
                error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
                return jsonify(error_msg), 400
        except Exception as wallet_error:
            error_msg = {"message": "Wallet Error!" + str(wallet_error)}
            return jsonify(error_msg), 400
    else:
        error_msg = {"message": "wrong user type"}
        return jsonify(error_msg), 400


# Grant Manager Account
@app.route('/grant_creator/create_manager', methods=["POST"])
def create_manager():

    try:
        # Get details of the user
        user_details = request.get_json()
        address = user_details['wallet_address']
        user_app_id = user_details['user_app_id']
        usertype = user_details['user_type']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    # check details of the user
    user_type = check.check_user(usertype)
    if user_type == "Approved":
        try:
            if CommonFunctions.check_balance(address, 1000):
                # give the user id for the user
                try:
                    usertxn = grant_creator.grant_manager_app(algod_client, user_app_id, usertype)
                    return jsonify(usertxn), 200
                except Exception as error:
                    return jsonify({"message": str(error)}), 500
            else:
                error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
                return jsonify(error_msg), 400
        except Exception as wallet_error:
            error_msg = {"message": "Wallet Error!" + str(wallet_error)}
            return jsonify(error_msg), 400
    else:
        error_msg = {"message": "wrong user type"}
        return jsonify(error_msg), 400


# remove manager
@app.route('/grant_creator/manager/remove', methods=["POST"])
def create_grant():
    try:
        # Get details of the user
        grant_details = request.get_json()
        address = grant_details['wallet_address']
        creator_app_id = grant_details['user_app_id']
        manager_app_id = grant_details['manager_user_app_id']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(address, 1000):
            # give the user id for the user
            try:
                usertxn = grant_creator.delete_manager(algod_client, creator_app_id, manager_app_id)
                return jsonify(usertxn), 200
            except Exception as error:
                return jsonify({"message": str(error)}), 500
        else:
            error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
            return jsonify(error_msg), 400
    except Exception as wallet_error:
        error_msg = {"message": "Wallet Error!" + str(wallet_error)}
        return jsonify(error_msg), 400


# Create Grant
@app.route('/grant_creator/grant/create_grant', methods=["POST"])
def create_grant():
    try:
        # Get details of the user
        grant_details = request.get_json()
        address = grant_details['wallet_address']
        user_app_id = grant_details['user_app_id']
        title = grant_details['title']
        duration = grant_details['duration']
        min_grant = grant_details['min_grant']
        max_grant = grant_details['max_grant']
        total_grants = grant_details['total_grants']
        total_budget = grant_details['total_budget']
        grant_end_date = grant_details['grant_end_date']
        ESG = grant_details['ESG']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(address, 1000):
            # give the user id for the user
            try:
                usertxn = grant_creator.grant_app(algod_client, user_app_id, title, duration, min_grant, max_grant,
                                                  total_grants, total_budget, grant_end_date, ESG)
                return jsonify(usertxn), 200
            except Exception as error:
                return jsonify({"message": str(error)}), 500
        else:
            error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
            return jsonify(error_msg), 400
    except Exception as wallet_error:
        error_msg = {"message": "Wallet Error!" + str(wallet_error)}
        return jsonify(error_msg), 400


# Edit Grant Details
@app.route('/grant_creator/grant/edit_grant', methods=["POST"])
def update_grant():
    try:
        # Get details of the user
        grant_details = request.get_json()
        address = grant_details['wallet_address']
        user_app_id = grant_details['user_app_id']
        grant_app_id = grant_details['grant_app_id']
        title = grant_details['title']
        duration = grant_details['duration']
        min_grant = grant_details['min_grant']
        max_grant = grant_details['max_grant']
        total_grants = grant_details['total_grants']
        total_budget = grant_details['total_budget']
        grant_end_date = grant_details['grant_end_date']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(address, 1000):
            # give the user id for the user
            try:
                usertxn = grant_creator.edit_grant(algod_client, user_app_id, title, duration, min_grant, max_grant,
                                                   total_grants, total_budget, grant_end_date, grant_app_id)
                return jsonify(usertxn), 200
            except Exception as error:
                return jsonify({"message": str(error)}), 500
        else:
            error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
            return jsonify(error_msg), 400
    except Exception as wallet_error:
        error_msg = {"message": "Wallet Error!" + str(wallet_error)}
        return jsonify(error_msg), 400


# admin approve/reject the grant
@app.route('/grant_creator/grant/admin_review', methods=['POST'])
def admin_review():
    try:
        # Get details of the user
        review_details = request.get_json()
        address = review_details['wallet_address']
        grant_app_id = review_details['grant_app_id']
        review = review_details['review']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(address, 1000):
            # give the user id for the user
            try:
                usertxn = grant_creator.admin_grant_review(algod_client, address, review, grant_app_id)
                return jsonify(usertxn), 200
            except Exception as error:
                return jsonify({"message": str(error)}), 500
        else:
            error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
            return jsonify(error_msg), 400
    except Exception as wallet_error:
        error_msg = {"message": "Wallet Error!" + str(wallet_error)}
        return jsonify(error_msg), 400


# Submit Application buy the grant applicant for grant
@app.route('/grant_applicant/submit_application', methods=["POST"])
def applicant_submit_application():

    try:
        # Get details of the user
        application_details = request.get_json()
        address = application_details['wallet_address']
        user_app_id = application_details['user_app_id']
        mile1 = application_details['mile1']
        mile2 = application_details['mile2']
        req_funds = application_details['req_funds']
        grant_app_id = application_details['grant_app_id']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(address, 1000):
            # give the user id for the user
            try:
                usertxn = grant_applicant.application_app(algod_client, address, user_app_id, mile1, mile2, req_funds, grant_app_id)
                return jsonify(usertxn), 200
            except Exception as error:
                return jsonify({"message": str(error)}), 500
        else:
            error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
            return jsonify(error_msg), 400
    except Exception as wallet_error:
        error_msg = {"message": "Wallet Error!" + str(wallet_error)}
        return jsonify(error_msg), 400


# Approve applicant's Application
@app.route('/grant_creator/grant/approve_application', methods=['POST'])
def approve_application():
    try:
        # Get details of the user
        approval_details = request.get_json()
        wallet_address = approval_details['wallet_address']
        application_app_id = approval_details['application_app_id']
        user_app_id = approval_details['user_app_id']
        grant_app_id = approval_details['grant_app_id']

    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(wallet_address, 1000):
            # give the user id for the user
            try:
                usertxn = grant_creator.approve_grant_application(algod_client, wallet_address, application_app_id, user_app_id, grant_app_id)
                return jsonify(usertxn), 200
            except Exception as error:
                return jsonify({"message": str(error)}), 500
        else:
            error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
            return jsonify(error_msg), 400
    except Exception as wallet_error:
        error_msg = {"message": "Wallet Error!" + str(wallet_error)}
        return jsonify(error_msg), 400


# Approve Applicant's Milestone 1 by Grant Creator/Manager
@app.route('/grant_creator/grant/approve_milestone_1', methods=['POST'])
def approve_milestone_1():
    try:
        # Get details of the user
        milestone_details = request.get_json()
        wallet_address = milestone_details['wallet_address']
        application_app_id = milestone_details['application_app_id']
        user_app_id = milestone_details['user_app_id']

    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(wallet_address, 1000):
            # give the user id for the user
            try:
                usertxn = grant_creator.milestone_1_approval(algod_client, wallet_address, application_app_id, user_app_id)
                return jsonify(usertxn), 200
            except Exception as error:
                return jsonify({"message": str(error)}), 500
        else:
            error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
            return jsonify(error_msg), 400
    except Exception as wallet_error:
        error_msg = {"message": "Wallet Error!" + str(wallet_error)}
        return jsonify(error_msg), 400


# Approve Applicant's Milestone 2 by Grant Creator/Manager
@app.route('/grant_creator/grant/approve_milestone_2', methods=['POST'])
def approve_milestone_2():
    try:
        # Get details of the user
        milestone_details = request.get_json()
        wallet_address = milestone_details['wallet_address']
        application_app_id = milestone_details['application_app_id']
        user_app_id = milestone_details['user_app_id']

    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(wallet_address, 1000):
            # give the user id for the user
            try:
                usertxn = grant_creator.milestone_2_approval(algod_client, wallet_address, application_app_id, user_app_id)
                return jsonify(usertxn), 200
            except Exception as error:
                return jsonify({"message": str(error)}), 500
        else:
            error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
            return jsonify(error_msg), 400
    except Exception as wallet_error:
        error_msg = {"message": "Wallet Error!" + str(wallet_error)}
        return jsonify(error_msg), 400


# Reject Applicant's Milestone 1/2 by Grant Creator/Manager
@app.route('/grant_creator/grant/milestone_reject', methods=['POST'])
def milestone_rejected():
    try:
        # Get details of the user
        milestone_details = request.get_json()
        wallet_address = milestone_details['wallet_address']
        application_app_id = milestone_details['application_app_id']
        user_app_id = milestone_details['user_app_id']

    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(wallet_address, 1000):
            # give the user id for the user
            try:
                usertxn = grant_creator.milestone_rejected(algod_client, wallet_address, application_app_id, user_app_id)
                return jsonify(usertxn), 200
            except Exception as error:
                return jsonify({"message": str(error)}), 500
        else:
            error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
            return jsonify(error_msg), 400
    except Exception as wallet_error:
        error_msg = {"message": "Wallet Error!" + str(wallet_error)}
        return jsonify(error_msg), 400


# running the API, on Port: 3000
if __name__ == "__main__":
    app.run(debug=True, port=3000)
