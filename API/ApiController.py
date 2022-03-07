from flask import Flask
import API.connection
import transcations.CreateAccount as trans

app = Flask(__name__)

algod_client = API.connection.algo_conn()


@app.route('/createAccount/<string:name>/<string:usertype>/<string:email>/<string:password>', methods=["POST"])
def create_account(name, usertype, email, password):
    appId = trans.create_app(algod_client, name, usertype, email, password)
    return appId


if __name__ == "__main__":
    # table_creation()
    app.run(debug=True)
