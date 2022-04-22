from flask import Flask, request
import API.connection
import utilities.check
import transactions.admin
import transactions.creator_investor
import transactions.indexer
import transactions.create_update_account


app = Flask(__name__)

# Setting up connection with algorand client
algod_client = API.connection.algo_conn()


# Create unique id for respective accounts created.
@app.route('/create_account', methods=["POST"])
def create_account():
    # Get details of the user
    user_details = request.get_json()
    username = user_details['username']
    usertype = user_details['user_type']
    email = user_details['email']

    # check details of the user
    name = utilities.check.check_username(username)
    user_type = utilities.check.check_user(usertype)
    email_id = utilities.check.check_email(email)
    if name == "Approved" and user_type == "Approved" and email_id == "Approved":
        # give the user id for the user
        userID = transactions.create_update_account.create_app(algod_client, username, usertype, email)
        return "Username registration successful with user id: {}".format(userID)
    else:
        lst_error = {"Username": name, "User Type": user_type, "Email": email_id}
        return lst_error


# create unique id for admin user
@app.route('/create_admin_account', methods=['POST'])
def create_admin_account():
    # Get details of the admin
    user_details = request.get_json()
    username = user_details['username']
    usertype = user_details['user_type']
    email = user_details['email']
    password = user_details['password']

    # check details of the admin
    name = utilities.check.check_username(username)
    user_type = utilities.check.check_admin(usertype)
    email_id = utilities.check.check_email(email)
    if name == "Approved" and user_type == "Approved" and email_id == "Approved":
        # give the admin id for the admin
        userID = transactions.admin.create_admin_account(algod_client, username, usertype, email, password)
        return "Admin registration successful with admin user id: {}".format(userID)
    else:
        lst_error = {"Username": name, "User Type": user_type, "Email": email_id}
        return lst_error


# Updating user details
@app.route('/update_account', methods=['POST'])
def update_user():
    # Get details of the user
    user_details = request.get_json()
    user_passphrase = user_details['user_passphrase']
    user_id = user_details['user_id']
    username = user_details['username']
    usertype = user_details['user_type']
    email = user_details['email']

    # check details of the user
    name = utilities.check.check_username(username)
    user_type = utilities.check.check_user(usertype)
    email_id = utilities.check.check_email(email)
    if name == "Approved" and user_type == "Approved" and email_id == "Approved":
        # give the user id for the user
        userID = transactions.create_update_account.update_user(algod_client, user_passphrase, user_id,
                                                                username, usertype, email)
        return "User updated successful with user id: {}".format(userID)
    else:
        lst_error = {"Username": name, "User Type": user_type, "Email": email_id}
        return lst_error


# updating admin
@app.route('/update_admin', methods=['POST'])
def update_admin():
    # Get details of the admin
    user_details = request.get_json()
    admin_passphrase = user_details['admin_passphrase']
    admin_id = user_details['admin_id']
    username = user_details['username']
    usertype = user_details['user_type']
    email = user_details['email']
    password = user_details['password']

    # check details of the user
    name = utilities.check.check_username(username)
    user_type = utilities.check.check_admin(usertype)
    email_id = utilities.check.check_email(email)
    if name == "Approved" and user_type == "Approved" and email_id == "Approved":
        # give the admin id for the user
        userID = transactions.admin.update_admin(algod_client, admin_passphrase, admin_id,
                                                 username, usertype, email, password)
        return "admin updated successful with admin user id: {}".format(userID)
    else:
        lst_error = {"Username": name, "User Type": user_type, "Email": email_id}
        return lst_error


# Creating a Campaign id for each campaign created by accounts.
@app.route('/create_campaign', methods=["POST"])
def create_campaign():
    # get details of the campaign to create
    campaign_details = request.get_json()
    your_passphrase = campaign_details['creator_passphrase']
    title = campaign_details['title']
    description = campaign_details['description']
    category = campaign_details['category']
    start_time = campaign_details['start_time']
    end_time = campaign_details['end_time']
    fund_category = campaign_details['fund_category']
    fund_limit = campaign_details['fund_limit']
    reward_type = campaign_details['reward_type']
    country = campaign_details['country']

    # pass the campaign details to the algorand
    campaignID = transactions.creator_investor.create_app(algod_client, your_passphrase, title, description,
                                                          category, start_time, end_time, fund_category,
                                                          fund_limit, reward_type, country)
    return campaignID


# update the existing campaign
@app.route('/update_campaign', methods=['POST'])
def update_campaign_details():
    # get details of the campaign to update
    campaign_details = request.get_json()
    your_passphrase = campaign_details['creator_passphrase']
    campaignID = campaign_details['campaign_id']
    title = campaign_details['title']
    description = campaign_details['description']
    category = campaign_details['category']
    start_time = campaign_details['start_time']
    end_time = campaign_details['end_time']
    fund_category = campaign_details['fund_category']
    fund_limit = campaign_details['fund_limit']
    reward_type = campaign_details['reward_type']
    country = campaign_details['country']

    # pass the campaign details to the algorand
    campaignID = transactions.creator_investor.update_campaign(algod_client, your_passphrase, campaignID, title,
                                                               description, category, start_time, end_time,
                                                               fund_category, fund_limit, reward_type, country)
    return "Campaign details updated with campaign id {}".format(campaignID)


# Group Transaction: (Call admin app and mint NFT)
@app.route('/create_asset', methods=["POST"])
def mint_nft():
    # get the details of the campaign to mint asset
    campaign_details = request.get_json()
    admin_id = campaign_details['admin_id']
    admin_passphrase = campaign_details['admin_passphrase']
    usertype = campaign_details['usertype']
    password = campaign_details['password']
    asset_amount = campaign_details['asset_amount']
    unit_name = campaign_details['unit_name']
    asset_name = campaign_details['asset_name']
    file_path = campaign_details['url']

    # pass the details to algorand to mint asset
    asset_id = transactions.admin.admin_asset(algod_client, admin_passphrase, usertype, password, admin_id,
                                              asset_amount, unit_name, asset_name, file_path)
    return "Minted NFT id: {}".format(asset_id)


# Transfer NFT from admin to campaign creator
@app.route('/transfer_asset', methods=["POST"])
def transfer_nft():
    # get the details for transferring the NFT
    transfer_details = request.get_json()
    admin_passphrase = transfer_details['admin_passphrase']
    asset_id = transfer_details['asset_id']
    campaign_id = transfer_details['campaign_id']
    campaign_creator_address = transfer_details['campaign_creator_address']
    nft_amount = transfer_details['nft_amount']

    # send the details to transfer NFT
    txn_details = transactions.creator_investor.call_nft_transfer(algod_client, admin_passphrase, asset_id,
                                                                  campaign_id, campaign_creator_address, nft_amount)
    return txn_details


# Transfer NFT from Campaign Creator to Investor
@app.route('/creator_investor', methods=["POST"])
def creator_investor():
    # getting the transaction details
    transfer_details = request.get_json()
    investor_passphrase = transfer_details['investor_passphrase']
    creator_passphrase = transfer_details['creator_passphrase']
    asset_id = transfer_details['asset_id']
    asset_amount = transfer_details['asset_amount']

    # send the details for transaction to occur
    txn_details = transactions.creator_investor.nft_creator_investor(algod_client, investor_passphrase,
                                                                     creator_passphrase, asset_id, asset_amount)
    return txn_details


# destroy asset, Group transaction: (campaign call app and destroy asset)
@app.route('/burn_asset', methods=["POST"])
def burnAsset():
    asset_details = request.get_json()
    creator_passphrase = asset_details['creator_passphrase']
    asset_id = asset_details['Asset_id']
    campaignID = asset_details['CampaignID']
    burnAssetTxn = transactions.creator_investor.call_asset_destroy(algod_client, creator_passphrase,
                                                                    asset_id, campaignID)
    return burnAssetTxn


# Investor Participating in Campaign by investing.
@app.route('/participating', methods=["POST"])
def participation():
    # get the details of investor participation's
    participation_details = request.get_json()
    your_passphrase = participation_details['investor_passphrase']
    campaignID = participation_details['campaign_id']
    investment = participation_details['amount']
    # pass the details to algorand to give the transaction id
    app_id = transactions.creator_investor.update_app(algod_client, your_passphrase, campaignID, investment)
    participationID = transactions.creator_investor.call_app(algod_client, your_passphrase, campaignID, investment)
    return "Participation successful in campaign {} with transaction id {}".format(app_id, participationID)


# Creator Pull out the investment that was done by the investors in the particular campaign
@app.route('/pull_investment', methods=["POST"])
def pull_investment():
    # get the details from the user
    investment_details = request.get_json()
    creator_passphrase = investment_details['creator_passphrase']
    campaignID = investment_details['campaign_id']
    pull = investment_details['amount']

    # pass the details to the algorand to run the transaction
    pullID = transactions.creator_investor.pull_investment(algod_client, creator_passphrase, campaignID, pull)
    return pullID


# Get total NFT minted by Admin
@app.route('/total_nft')
def totalNFT():
    admin_info = request.get_json()
    admin = admin_info['admin_address']
    all_nft = transactions.indexer.total_assets_by_admin(admin)
    return all_nft


# Get the account information of particular account
@app.route('/account_info')
def account_information():
    account_data = request.get_json()
    address = account_data['account']
    account = transactions.indexer.account_info(address)
    return account


# running the API
if __name__ == "__main__":
    app.run(debug=True)
