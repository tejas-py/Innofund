from flask import Flask, request, jsonify
from flask_cors import CORS
from utilities import check, CommonFunctions
from transactions import admin, creator_investor, indexer, create_update_account
import connection

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
    milestone_title_lst = (milestone['milestone_title']['1'], milestone['milestone_title']['2'], milestone['milestone_title']['3'])
    milestone_list = (milestone['milestone_number']['1'], milestone['milestone_number']['2'], milestone['milestone_number']['3'])
    end_time_lst = (milestone['end_time_milestone']['1'], milestone['end_time_milestone']['2'], milestone['end_time_milestone']['3'])

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
    milestone_app_id_lst = (milestone['milestone_app_id']['1'], milestone['milestone_app_id']['2'], milestone['milestone_app_id']['3'])
    milestone_title_lst = (milestone['milestone_title']['1'], milestone['milestone_title']['2'], milestone['milestone_title']['3'])
    milestone_list = (milestone['milestone_number']['1'], milestone['milestone_number']['2'], milestone['milestone_number']['3'])
    end_time_lst = (milestone['end_time_milestone']['1'], milestone['end_time_milestone']['2'], milestone['end_time_milestone']['3'])

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
                # pass the details
                reject_campaign_id_txn = creator_investor.block_reason(algod_client, address, campaignID, reason)
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
    campaign_app_id = user_delete['campaign_app_id']
    nft_id = int(user_delete['nft_id'])
    milestone_app_id = user_delete['milestone_app_id']
    address = CommonFunctions.get_address_from_application(campaign_app_id)

    # creating the list of milestone app id
    milestones_lst = (milestone_app_id['1'], milestone_app_id['2'], milestone_app_id['3'])

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
                    deleted_campaignID_txn = creator_investor.nft_delete(algod_client, campaign_app_id, nft_id,
                                                                         milestones_lst)
                    return jsonify(deleted_campaignID_txn), 200
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


# end milestone
@app.route('/end_milestone', methods=['POST'])
def milestone_end():
    # get the details
    milestone_details = request.get_json()
    milestone_app_id = milestone_details['milestone_app_id']
    milestone_title = milestone_details['milestone_title']
    milestone_no = milestone_details['milestone_number']

    end_txn = creator_investor.end_milestone(algod_client, milestone_app_id, milestone_title, milestone_no)

    return jsonify(end_txn)


# admin verifies the milestone
@app.route('/verify_milestone', methods=['POST'])
def check_milestone():
    # get the details
    verification_details = request.get_json()
    note = verification_details['note']
    check_milestone_app_id = verification_details['check_milestone_app_id']

    # second milestone
    milestone_app_id = verification_details['milestone_app_id']
    milestone_title = verification_details['milestone_title']
    milestone_no = verification_details['milestone_number']

    approve_lst = ['approve', 'APPROVE', 'Approve']

    if note in approve_lst:
        grp_txn = creator_investor.approve_milestone(algod_client, note, check_milestone_app_id, milestone_app_id,
                                                     milestone_title, milestone_no)
        return jsonify(grp_txn)
    else:
        txn = creator_investor.reject_milestone(algod_client, note, milestone_app_id)
        return jsonify(txn)


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
#     # get the details of the campaign to mint asset
#     mint_asset = request.get_json()
#     app_id = mint_asset['app_id']
#     user_name = mint_asset['name']
#     usertype = mint_asset['user_type']
#     unit_name = mint_asset['unit_name']
#     asset_name = mint_asset['asset_name']
#     total_amount = mint_asset['amount']
#     picture = mint_asset['image_hash']
#     meta_data = mint_asset['meta_data']
#
#     # get the wallet address from the user application id
#     address = CommonFunctions.get_address_from_application(app_id)
#
#     # create a blank array for the transactions
#     asset_create_txn = []
#
#     if len(unit_name) == total_amount and len(asset_name) == total_amount \
#             and len(picture) == total_amount and len(meta_data) == total_amount:
#         for unit, name, image, meta in zip(unit_name, asset_name, picture, meta_data):
#             print(unit_name[unit], asset_name[name], picture[image])
#             try:
#                 if CommonFunctions.check_balance(address, 1000):
#                     try:
#                         # pass the details to algorand to mint asset
#                         asset_txn = admin.admin_asset(algod_client, user_name, usertype, app_id, unit_name[unit],
#                                                       asset_name[name], picture[image], meta_data[meta])
#                         asset_create_txn.append(asset_txn)
#                     except Exception as error:
#                         return str(error), 500
#                 else:
#                     return f"To Mint NFT, Minimum Balance should be 1000 microAlgos", 400
#             except Exception as wallet_error:
#                 return f"Check Wallet Address, Error: {wallet_error}", 400
#         return jsonify(asset_create_txn), 200
#     else:
#         return "Please check the total amount of NFT and other fields.", 400


# Opt-in to NFT
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
@app.route('/claim_nft', methods=["POST"])
def clamming_nft():
    # getting the transaction details
    transfer_details = request.get_json()
    investor_address = transfer_details['investor_wallet_address']
    asset_id = transfer_details['NFT_asset_id']
    asset_amount = transfer_details['asset_amount']
    campaign_app_id = transfer_details['campaign_app_id']

    try:
        if CommonFunctions.check_balance(investor_address, 3000):
            try:
                # send the details for transaction to occur
                txn_details = creator_investor.claim_nft(algod_client, investor_address,
                                                                    asset_id, asset_amount, campaign_app_id)
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
    investment = participation_details['amount']
    investor_account = participation_details['investor_wallet_address']
    address = CommonFunctions.get_address_from_application(campaignID)

    try:
        if CommonFunctions.check_balance(address, 3000):
            # pass the details to algorand to give the transaction id
            try:
                participationID = creator_investor.update_call_app(algod_client, campaignID,
                                                                       investment, investor_account)
                return jsonify(participationID), 200
            except Exception as error:
                return str(error), 500
        else:
            return "To Participate in a campaign, Minimum Balance should be 3000 microAlgos", 400
    except Exception as wallet_error:
        return f"Check Wallet Address, Error: {wallet_error}", 400


# Creator Pull out the investment that was done by the investors in the particular campaign
@app.route('/pull_investment', methods=["POST"])
def pull_investment():
    # get the details from the user
    investment_details = request.get_json()
    creator_passphrase = investment_details['creator_passphrase']
    campaignID = investment_details['campaign_app_id']
    pull = investment_details['amount']

    # pass the details to the algorand to run the transaction
    pullID = creator_investor.pull_investment(algod_client, creator_passphrase, campaignID, pull)
    txn_details = {"transaction_id": pullID}
    return jsonify(txn_details)


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


# Get the account information of particular account
@app.route('/account_info')
def account_information():
    account_data = request.get_json()
    address = account_data['wallet_address']
    try:
        account = indexer.account_info(address)
        return jsonify(account), 200
    except Exception as error:
        return str(error), 500


# running the API
if __name__ == "__main__":
    app.run(debug=True, port=4000)
