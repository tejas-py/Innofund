from flask import Flask
import API.connection
import transcations.CreateAccount as account
import transcations.createCampaign
import re
import utilities.check

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
    if name and usertype and email_id == "Approved":
        userID = account.create_app(algod_client, username, usertype, email)
        return "Username registration successful with user id: {}".format(userID)
    else:
        lst_error = {"Username": name, "User Type": user_type, "Email": email_id}
        return lst_error


# Creating a Campaign id for each campaign created by accounts.
@app.route('/createCampaign/<string:your_passphrase>/<string:title>/<string:description>'
           '/<string:category>/<int:start_time>/<int:end_time>/<string:fund_category>'
           '/<string:fund_limit>/<string:country>',
           methods=["POST"])
def create_campaign(your_passphrase,  title, description,
                    category, start_time, end_time, fund_category,
                    fund_limit, country):
    campaignID = transcations.createCampaign.create_app(algod_client, your_passphrase,  title, description,
                                                        category, start_time, end_time, fund_category,
                                                        fund_limit, country)
    return campaignID


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
