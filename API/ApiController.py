from flask import Flask
import API.connection
import transcations.CreateAccount as account
import transcations.createCampaign as campaign
import transcations.escrow_creator
import transcations.txn_escrow
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


# Transaction of algos, Investor to escrow.
@app.route('/escrow_trasaction_details/<string:passphrase>/<int:amount>')
def escrow_transaction(passphrase, amount):
    try:
        txnID = transcations.txn_escrow.transfer(passphrase, amount)
        if re.search("[0-9]+[A-Z]", txnID):
            return "Transaction of {} was successful. Transaction ID: {}".format(amount, txnID)
        else:
            return "Transaction was not successful."
    except Exception:
        return "Transaction was not successful, please check your passphrase."


# Transaction of algos, Escrow to Creator.
@app.route('/creator_escrow_tnx/<string:your_address>/<int:amount>')
def creator_escrow(your_address, amount):
    txnID = transcations.escrow_creator.transfer(your_address, amount)
    if re.search("[0-9]+[A-Z]", txnID):
        return "Transaction of {} was successful. Transaction ID: {}".format(amount, txnID)
    else:
        return "Transaction was not successful."


if __name__ == "__main__":
    # table_creation()
    app.run(debug=True)
