from flask import Flask, request
import API.connection
import transcations.CreateAccount as account
import transcations.createCampaign
import transcations.UpdateAccount
import transcations.AssetCampaignCall
import utilities.check
import utilities.CommonFunctions as comFunc

app = Flask(__name__)

algod_client = API.connection.algo_conn()


# Create unique id for respective accounts created.
@app.route('/createAccount/', methods=["POST"])
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
@app.route('/updateAccount/<string:user_passphrase>/<int:user_id>')
def update_user(user_passphrase, user_id):
    update_user_id = transcations.UpdateAccount.update_user(algod_client, user_passphrase,
                                                            user_id)
    return update_user_id


# Creating a Campaign id for each campaign created by accounts.
@app.route('/createCampaign', methods=["POST"])
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
    campaignID = transcations.createCampaign.create_app(algod_client, your_passphrase,  title, description,
                                                        category, start_time, end_time, fund_category,
                                                        fund_limit, reward_type, country)
    return campaignID


# Rewards
@app.route('/campaign_rewards/<string:campaign_id>/<string:check_address>')
def rewards(campaign_id, check_address):
    result = comFunc.Check_app_creator_address(campaign_id, check_address)
    return result


# create asset (Group Transaction, Call app and create asset )
@app.route('/createAsset', methods=["POST"])
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
    asset_id = transcations.AssetCampaignCall.call_asset(algod_client, private_key, campaignID, asset_amount,
                                                         unit_name, asset_name, file_path)
    return asset_id


# destroy asset (group txn, destroy and call app )
@app.route('/burnAsset', methods=["POST"])
def burnAsset():
    asset_details = request.get_json()
    private_key = asset_details['Private_key']
    asset_id = asset_details['Asset_id']
    campaignID = asset_details['CampaignID']
    burnAssetTxn = transcations.AssetCampaignCall.call_asset_destroy(algod_client, private_key, asset_id, campaignID)
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
    participationID = transcations.createCampaign.call_app(algod_client, your_passphrase, campaignID, investment)
    return participationID


# Creator Pull out the investment that was done by the investors in the particular campaign
@app.route('/pull_investment', methods=["POST"])
def pull_investment():
    # get the details from the user
    investment_details = request.get_json()
    creator_passphrase = investment_details['creator_passphrase']
    campaignID = investment_details['campaign_id']
    pull = investment_details['amount']

    # pass the details to the algorand to run the transaction
    pullID = transcations.createCampaign.pull_investment(algod_client, creator_passphrase, campaignID, pull)
    return pullID


if __name__ == "__main__":
    # table_creation()
    app.run(debug=True)
