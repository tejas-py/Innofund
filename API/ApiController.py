from flask import Flask
import transcations.CreateAccount as trans
from API import connection

app = Flask(__name__)

algod_client = connection.algo_conn()


@app.route('/createAccount', methods=["POST"])
def create_account():
    appId = trans.create_app(algod_client, "")
    return appId


if __name__ == "__main__":
    # table_creation()
    app.run(debug=True)
