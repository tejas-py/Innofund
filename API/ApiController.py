from flask import Flask
import transcations.CreateAccount as trans
from API import connection
from utilities.accounts import account

app = Flask(__name__)

algod_client = connection.algo_conn()


@app.route('/createAccount/<string:name>/<string:usertype>/<string:email>/<string:password>', methods=["POST"])
def create_account(name, usertype, email, password):
    appId = trans.create_app(algod_client, account(), name, usertype, email, password)
    return appId


if __name__ == "__main__":
    # table_creation()
    app.run(debug=True)
