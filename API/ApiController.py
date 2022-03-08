from flask import Flask
import API.connection
import transcations.CreateAccount as account
import transcations.createCampaign as campaign
import transcations.escrow_creator
import transcations.txn_escrow
import re

app = Flask(__name__)

algod_client = API.connection.algo_conn()


# Create unique id for respective accounts created.
@app.route('/createAccount/'
           '<string:name>'
           '/<string:usertype>'
           '/<string:email>'
           '/<string:password>',
           methods=["POST"])
def create_account(name, usertype, email, password):
    userID = account.create_app(algod_client, name, usertype, email, password)
    return userID


# Creating a Campaign id for each campaign created by accounts.
@app.route('/createCampaign/<string:your_passphrase>/<string:creator>/<string:title>'
           '/<string:campaign_type>/<string:description>'
           '/<string:start_time>/<string:end_time>/<string:fund_limit>',
           methods=["POST"])
def create_campaign(your_passphrase, creator, title, campaign_type,
                    description, start_time, end_time,
                    fund_limit):
    campaignID = campaign.create_app(algod_client, your_passphrase, creator, title,
                                     campaign_type, description, start_time,
                                     end_time, fund_limit)
    return campaignID


# Transaction of algos, Investor to escrow.
@app.route('/escrow_trasaction_details/<string:passphrase>')
def escrow_transaction(passphrase):
    try:
        txnID = transcations.txn_escrow.transfer(passphrase)
        if re.search("[0-9]+[A-Z]", txnID):
            return "Transaction was successful. Transaction ID: {}".format(txnID)
        else:
            return "Transaction was not successful."
    except Exception:
        return "Transaction was not successful, please check your passphrase."


# Transaction of algos, Escrow to Creator.
@app.route('/creator_escrow_tnx/<string:your_address>')
def creator_escrow(your_address):
    txnID = transcations.escrow_creator.transfer(your_address)
    if re.search("[0-9]+[A-Z]", txnID):
        return "Transaction was successful. Transaction ID: {}".format(txnID)
    else:
        return "Transaction was not successful."


if __name__ == "__main__":
    # table_creation()
    app.run(debug=True)
