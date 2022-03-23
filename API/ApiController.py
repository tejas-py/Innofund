from flask import Flask, request
import API.connection
import transcations.CreateAccount as account
import transcations.createCampaign
import transcations.UpdateAccount
import transcations.burn_asset
import transcations.AssetCampaignCall
import utilities.check
import utilities.CommonFunctions as comFunc

app = Flask(__name__)

algod_client = API.connection.algo_conn()


# Create unique id for respective accounts created.
@app.route('/createAccount/'
           '<string:username>'
           '/<string:usertype>'
           '/<string:email>',
           methods=["POST"])
def create_account(username, usertype, email):
    name = utilities.check.check_username(username)
    user_type = utilities.check.check_user(usertype)
    email_id = utilities.check.check_email(email)
    if name == "Approved" and user_type == "Approved" and email_id == "Approved":
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
@app.route('/createCampaign/<string:your_passphrase>/<string:title>/<string:description>'
           '/<string:category>/<int:start_time>/<int:end_time>/<string:fund_category>'
           '/<string:fund_limit>/<string:reward_type>/<string:country>',
           methods=["POST"])
def create_campaign(your_passphrase,  title, description,
                    category, start_time, end_time, fund_category,
                    fund_limit, reward_type, country):
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
    campaign_details = request.get_json()
    campaignID = campaign_details['CampaignID']
    private_key = campaign_details['Key']
    asset_amount = campaign_details['asset_amount']
    unit_name = campaign_details['unit_name']
    asset_name = campaign_details['asset_name']
    file_path = campaign_details['url']
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
@app.route('/participating/<string:your_passphrase>/<int:campaignID>/<int:investment>')
def participation(your_passphrase, campaignID, investment):
    participationID = transcations.createCampaign.call_app(algod_client, your_passphrase, campaignID, investment)
    return participationID


# Creator Pull out the investment that was done by the investors in the particular campaign
@app.route('/pull_investment/<string:creator_passphrase>/<int:campaignID>/<int:pull>')
def pull_investment(creator_passphrase, campaignID, pull):
    pullID = transcations.createCampaign.pull_investment(algod_client, creator_passphrase, campaignID, pull)
    return pullID


if __name__ == "__main__":
    # table_creation()
    app.run(debug=True)
