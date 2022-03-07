from flask import Flask
import transcations.CreateAccount as trans
from API import connection

from utilities.CommonFunctions import get_private_key_from_mnemonic

app = Flask(__name__)

algod_client = connection.algo_conn()


def account123():
    account1 = "couch unveil crush drastic staff peanut tooth code matrix drip jazz team ticket ring punch local patrol smile stay hobby maze swamp cash absent erupt"
    a1 = get_private_key_from_mnemonic(account1)
    return a1


@app.route('/createAccount/<string:name/string:usertype>', methods=["POST"])
def create_account(name, usertype):
    appId = trans.create_app(algod_client, account123(), name, usertype)
    return appId


if __name__ == "__main__":
    # table_creation()
    app.run(debug=True)
