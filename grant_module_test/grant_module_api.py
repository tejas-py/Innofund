from flask import Flask, request, jsonify
from flask_cors import CORS
from utilities import check, CommonFunctions
from grant_module_test import grant_applicant_test as grant_applicant
from grant_module_test import grant_creator_test as grant_creator
from API import connection

# defining the flask app and setting up cors
app = Flask(__name__)
cors = CORS(app, resources={
    r"/*": {"origin": "*"}
})

# Setting up connection with algorand client
algod_client = connection.algo_conn()


# Grant Creator Account
@app.route('/grant_creator/create_account', methods=['POST'])
def grant_creator_account():
    try:
        # Get details of the user
        creator_details = request.get_json()
        address = creator_details['wallet_address']
        mnemonic_keys = creator_details['mnemonic_keys']
        usertype = creator_details['user_type']
        organisation_name = creator_details['organisation_name']
        organisation_role = creator_details['organisation_role']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    # check details of the user
    user_type = check.check_user(usertype)
    if user_type == "Approved":
        try:
            if CommonFunctions.check_balance(address, 1000):
                # give the user id for the user
                try:
                    usertxn = grant_creator.grant_admin_app(algod_client, mnemonic_keys, organisation_name, organisation_role, usertype)
                    return jsonify(usertxn), 200
                except Exception as error:
                    return jsonify({"message": str(error)}), 500
            else:
                error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
                return jsonify(error_msg), 400
        except Exception as wallet_error:
            error_msg = {"message": "Wallet Error!" + str(wallet_error)}
            return jsonify(error_msg), 400
    else:
        error_msg = {"message": "wrong user type"}
        return jsonify(error_msg), 400


# Grant Applicant Account
@app.route('/grant_applicant/create_account', methods=["POST"])
def grant_applicant_account():

    try:
        # Get details of the user
        user_details = request.get_json()
        address = user_details['wallet_address']
        mnemonic_keys = user_details['mnemonic_keys']
        usertype = user_details['user_type']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    # check details of the user
    user_type = check.check_user(usertype)
    if user_type == "Approved":
        try:
            if CommonFunctions.check_balance(address, 1000):
                # give the user id for the user
                try:
                    usertxn = grant_applicant.grant_applicant_app(algod_client, mnemonic_keys, usertype)
                    return jsonify(usertxn), 200
                except Exception as error:
                    return jsonify({"message": str(error)}), 500
            else:
                error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
                return jsonify(error_msg), 400
        except Exception as wallet_error:
            error_msg = {"message": "Wallet Error!" + str(wallet_error)}
            return jsonify(error_msg), 400
    else:
        error_msg = {"message": "wrong user type"}
        return jsonify(error_msg), 400


# Grant Manager Account
@app.route('/grant_creator/create_manager', methods=["POST"])
def create_manager():

    try:
        # Get details of the user
        user_details = request.get_json()
        address = user_details['wallet_address']
        mnemonic_keys = user_details['mnemonic_keys']
        user_app_id = user_details['user_app_id']
        usertype = user_details['user_type']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    # check details of the user
    user_type = check.check_user(usertype)
    if user_type == "Approved":
        try:
            if CommonFunctions.check_balance(address, 1000):
                # give the user id for the user
                try:
                    usertxn = grant_creator.grant_manager_app(algod_client, mnemonic_keys, user_app_id, usertype)
                    return jsonify(usertxn), 200
                except Exception as error:
                    return jsonify({"message": str(error)}), 500
            else:
                error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
                return jsonify(error_msg), 400
        except Exception as wallet_error:
            error_msg = {"message": "Wallet Error!" + str(wallet_error)}
            return jsonify(error_msg), 400
    else:
        error_msg = {"message": "wrong user type"}
        return jsonify(error_msg), 400


# Create Grant
@app.route('/grant_creator/grant/create_grant', methods=["POST"])
def create_grant():
    try:
        # Get details of the user
        grant_details = request.get_json()
        address = grant_details['wallet_address']
        mnemonic_keys = grant_details['mnemonic_keys']
        user_app_id = grant_details['user_app_id']
        title = grant_details['title']
        duration = grant_details['duration']
        min_grant = grant_details['min_grant']
        max_grant = grant_details['max_grant']
        total_grants = grant_details['total_grants']
        total_budget = grant_details['total_budget']
        grant_end_date = grant_details['grant_end_date']
        ESG = grant_details['ESG']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(address, 1000):
            # give the user id for the user
            try:
                usertxn = grant_creator.grant_app(algod_client, mnemonic_keys, user_app_id, title, duration, min_grant, max_grant,
                                                  total_grants, total_budget, grant_end_date, ESG)
                return jsonify(usertxn), 200
            except Exception as error:
                return jsonify({"message": str(error)}), 500
        else:
            error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
            return jsonify(error_msg), 400
    except Exception as wallet_error:
        error_msg = {"message": "Wallet Error!" + str(wallet_error)}
        return jsonify(error_msg), 400


# Edit Grant Details
@app.route('/grant_creator/grant/edit_grant', methods=["POST"])
def update_grant():
    try:
        # Get details of the user
        grant_details = request.get_json()
        address = grant_details['wallet_address']
        mnemonic_keys = grant_details['mnemonic_keys']
        user_app_id = grant_details['user_app_id']
        grant_app_id = grant_details['grant_app_id']
        title = grant_details['title']
        duration = grant_details['duration']
        min_grant = grant_details['min_grant']
        max_grant = grant_details['max_grant']
        total_grants = grant_details['total_grants']
        total_budget = grant_details['total_budget']
        grant_end_date = grant_details['grant_end_date']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(address, 1000):
            # give the user id for the user
            try:
                usertxn = grant_creator.edit_grant(algod_client, mnemonic_keys, user_app_id, title, duration, min_grant, max_grant,
                                                   total_grants, total_budget, grant_end_date, grant_app_id)
                return jsonify(usertxn), 200
            except Exception as error:
                return jsonify({"message": str(error)}), 500
        else:
            error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
            return jsonify(error_msg), 400
    except Exception as wallet_error:
        error_msg = {"message": "Wallet Error!" + str(wallet_error)}
        return jsonify(error_msg), 400


# admin approve/reject the grant
@app.route('/grant_creator/grant/admin_review', methods=['POST'])
def admin_review():
    try:
        # Get details of the user
        review_details = request.get_json()
        address = review_details['wallet_address']
        mnemonic_keys = review_details['mnemonic_keys']
        grant_app_id = review_details['grant_app_id']
        review = review_details['review']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(address, 1000):
            # give the user id for the user
            try:
                usertxn = grant_creator.admin_grant_review(algod_client, mnemonic_keys, review, grant_app_id)
                return jsonify(usertxn), 200
            except Exception as error:
                return jsonify({"message": str(error)}), 500
        else:
            error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
            return jsonify(error_msg), 400
    except Exception as wallet_error:
        error_msg = {"message": "Wallet Error!" + str(wallet_error)}
        return jsonify(error_msg), 400


# Delete Grant
@app.route('/grant_creator/grant/delete', methods=['POST'])
def delete_grant():
    return None


# Submit Application buy the grant applicant for grant
@app.route('/grant_applicant/grant_application/submit_application', methods=["POST"])
def applicant_submit_application():

    try:
        # Get details of the user
        application_details = request.get_json()
        address = application_details['wallet_address']
        mnemonic_keys = application_details['mnemonic_keys']
        user_app_id = application_details['user_app_id']
        mile1 = application_details['mile1']
        mile2 = application_details['mile2']
        req_funds = application_details['req_funds']
        grant_app_id = application_details['grant_app_id']
    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(address, 1000):
            # give the user id for the user
            try:
                usertxn = grant_applicant.application_app(algod_client, address, mnemonic_keys, user_app_id, mile1, mile2, req_funds, grant_app_id)
                return jsonify(usertxn), 200
            except Exception as error:
                return jsonify({"message": str(error)}), 500
        else:
            error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
            return jsonify(error_msg), 400
    except Exception as wallet_error:
        error_msg = {"message": "Wallet Error!" + str(wallet_error)}
        return jsonify(error_msg), 400


# Edit Grant Application
@app.route('/grant_applicant/grant_application/edit_application', methods=['POST'])
def edit_application():
    return None


# Delete Grant Application
@app.route('/grant_applicant/grant_application/delete', methods=['POST'])
def delete_grant_application():
    return None


# Approve applicant's Application
@app.route('/grant_creator/grant/approve_application', methods=['POST'])
def approve_application():
    try:
        # Get details of the user
        approval_details = request.get_json()
        wallet_address = approval_details['wallet_address']
        mnemonic_keys = approval_details['mnemonic_keys']
        application_app_id = approval_details['application_app_id']
        user_app_id = approval_details['user_app_id']
        grant_app_id = approval_details['grant_app_id']

    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(wallet_address, 1000):
            # give the user id for the user
            try:
                usertxn = grant_creator.approve_grant_application(algod_client, mnemonic_keys, wallet_address, application_app_id, user_app_id, grant_app_id)
                return jsonify(usertxn), 200
            except Exception as error:
                return jsonify({"message": str(error)}), 500
        else:
            error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
            return jsonify(error_msg), 400
    except Exception as wallet_error:
        error_msg = {"message": "Wallet Error!" + str(wallet_error)}
        return jsonify(error_msg), 400


# Reject Applicant's Application
@app.route('/grant_creator/grant/reject_application', methods=['POST'])
def reject_application():
    return None


# Approve Applicant's Milestone 1 by Grant Creator/Manager
@app.route('/grant_creator/grant/approve_milestone_1', methods=['POST'])
def approve_milestone_1():
    try:
        # Get details of the user
        milestone_details = request.get_json()
        wallet_address = milestone_details['wallet_address']
        mnemonic_keys = milestone_details['mnemonic_keys']
        application_app_id = milestone_details['application_app_id']
        user_app_id = milestone_details['user_app_id']

    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(wallet_address, 1000):
            # give the user id for the user
            try:
                usertxn = grant_creator.milestone_1_approval(algod_client, mnemonic_keys, wallet_address, application_app_id, user_app_id)
                return jsonify(usertxn), 200
            except Exception as error:
                return jsonify({"message": str(error)}), 500
        else:
            error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
            return jsonify(error_msg), 400
    except Exception as wallet_error:
        error_msg = {"message": "Wallet Error!" + str(wallet_error)}
        return jsonify(error_msg), 400


# Approve Applicant's Milestone 2 by Grant Creator/Manager
@app.route('/grant_creator/grant/approve_milestone_2', methods=['POST'])
def approve_milestone_2():
    try:
        # Get details of the user
        milestone_details = request.get_json()
        wallet_address = milestone_details['wallet_address']
        mnemonic_keys = milestone_details['mnemonic_keys']
        application_app_id = milestone_details['application_app_id']
        user_app_id = milestone_details['user_app_id']

    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(wallet_address, 1000):
            # give the user id for the user
            try:
                usertxn = grant_creator.milestone_2_approval(algod_client, mnemonic_keys, wallet_address, application_app_id, user_app_id)
                return jsonify(usertxn), 200
            except Exception as error:
                return jsonify({"message": str(error)}), 500
        else:
            error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
            return jsonify(error_msg), 400
    except Exception as wallet_error:
        error_msg = {"message": "Wallet Error!" + str(wallet_error)}
        return jsonify(error_msg), 400


# Reject Applicant's Milestone 1/2 by Grant Creator/Manager
@app.route('/grant_creator/grant/reject_milestone', methods=['POST'])
def reject_milestone():
    try:
        # Get details of the user
        milestone_details = request.get_json()
        wallet_address = milestone_details['wallet_address']
        mnemonic_keys = milestone_details['mnemonic_keys']
        application_app_id = milestone_details['application_app_id']
        user_app_id = milestone_details['user_app_id']

    except Exception as error:
        return jsonify({'message': f'Payload Error! Key Missing: {error}'}), 500

    try:
        if CommonFunctions.check_balance(wallet_address, 1000):
            # give the user id for the user
            try:
                usertxn = grant_creator.milestone_rejected(algod_client, mnemonic_keys, wallet_address, application_app_id, user_app_id)
                return jsonify(usertxn), 200
            except Exception as error:
                return jsonify({"message": str(error)}), 500
        else:
            error_msg = {"message": "For Account Creation, Minimum Balance should be 1000 microAlgos"}
            return jsonify(error_msg), 400
    except Exception as wallet_error:
        error_msg = {"message": "Wallet Error!" + str(wallet_error)}
        return jsonify(error_msg), 400


# running the API
if __name__ == "__main__":
    app.run(debug=True, port=3002)
