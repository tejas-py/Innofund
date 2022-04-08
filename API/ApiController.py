from flask import Flask, request
import API.connection
import transactions.CreateAccount as account
import transactions.createCampaign
import transactions.UpdateAccount
import transactions.AssetCampaignCall
import transactions.update_campaign
import utilities.check
import utilities.CommonFunctions as comFunc

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
        userID = account.create_app(algod_client, username, usertype, email)
        return "Username registration successful with user id: {}".format(userID)
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
        userID = transactions.UpdateAccount.update_user(algod_client, user_passphrase, user_id,
                                                        username, usertype, email)
        return "User updated successful with user id: {}".format(userID)
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
    campaignID = transactions.createCampaign.create_app(algod_client, your_passphrase, title, description,
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
    campaignID = transactions.update_campaign.update_campaign(algod_client, your_passphrase, campaignID, title,
                                                              description, category, start_time, end_time,
                                                              fund_category, fund_limit, reward_type, country)
    return "Campaign details updated with campaign id {}".format(campaignID)


# Rewards
@app.route('/campaign_rewards/<string:campaign_id>/<string:check_address>')
def rewards(campaign_id, check_address):
    result = comFunc.Check_app_creator_address(campaign_id, check_address)
    return result


# create asset (Group Transaction, Call app and create asset )
@app.route('/create_asset', methods=["POST"])
def createAsset():
    # get the details of the campaign to mint asset
    campaign_details = request.get_json()
    campaignID = campaign_details['CampaignID']
    private_key = campaign_details['Key']
    asset_amount = campaign_details['asset_amount']
    unit_name = campaign_details['unit_name']
    asset_name = campaign_details['asset_name']
    file_path = campaign_details['url']

    # pass the details to algorand to mint asset
    asset_id = transactions.AssetCampaignCall.call_asset(algod_client, private_key, campaignID, asset_amount,
                                                         unit_name, asset_name, file_path)
    return asset_id


# destroy asset (group txn, destroy and call app )
@app.route('/burn_asset', methods=["POST"])
def burnAsset():
    asset_details = request.get_json()
    private_key = asset_details['Private_key']
    asset_id = asset_details['Asset_id']
    campaignID = asset_details['CampaignID']
    burnAssetTxn = transactions.AssetCampaignCall.call_asset_destroy(algod_client, private_key, asset_id, campaignID)
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
    app_id = transactions.createCampaign.update_app(algod_client, your_passphrase, campaignID, investment)
    participationID = transactions.createCampaign.call_app(algod_client, your_passphrase, campaignID, investment)
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
    pullID = transactions.createCampaign.pull_investment(algod_client, creator_passphrase, campaignID, pull)
    return pullID


# running the API
if __name__ == "__main__":
    # table_creation()
    app.run(debug=True)
