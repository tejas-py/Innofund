from flask import Flask
import API.connection
import transcations.CreateAccount as account
import transcations.createCampaign as campaign
import transcations.txn_escrow
import re

app = Flask(__name__)

algod_client = API.connection.algo_conn()


@app.route('/createAccount/'
           '<string:name>'
           '/<string:usertype>'
           '/<string:email>'
           '/<string:password>',
           methods=["POST"])
def create_account(name, usertype, email, password):
    userID = account.create_app(algod_client, name, usertype, email, password)
    return userID


@app.route('/createCampaign/'
           '<string:title>'
           '/<string:description>'
           '/<string:fund_limit>'
           '/<string:duration>',
           methods=["POST"])
def create_campaign(title, description, fund_limit, duration):
    campaignID = campaign.create_app(algod_client, title, description, fund_limit, duration)
    return campaignID


#Invester to escrow.
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


if __name__ == "__main__":
    # table_creation()
    app.run(debug=True)
