from flask import Flask
import API.connection
import transcations.CreateAccount as trans

app = Flask(__name__)

algod_client = API.connection.algo_conn()


@app.route('/createAccount/'
           '<string:name>'
           '/<string:usertype>'
           '/<string:email>'
           '/<string:password>',
           methods=["POST"])
def create_account(name, usertype, email, password):
    userID = trans.create_app(algod_client, name, usertype, email, password)
    return userID


@app.route('/createCampaign/'
           '<string:title>'
           '/<string:description>'
           '/<string:fund_limit>'
           '/<string:duration>',
           methods=["POST"])
def create_campaign(title, description, fund_limit, duration):
    campaignID = trans.create_app(algod_client, title, description, fund_limit, duration)
    return campaignID


if __name__ == "__main__":
    # table_creation()
    app.run(debug=True)
