import base64
import json
import operator
import re
from algosdk import encoding
from API import connection
import utilities.CommonFunctions

# connect to the indexer API
indexerConnection = connection.connect_indexer()


# get the transaction information for asset by an account
def get_minted_asset_transaction(address):

    # get address from app id
    # address = utilities.CommonFunctions.get_address_from_application(app_id)

    # get asset create transactions
    response = indexerConnection.search_transactions_by_address(address=address, txn_type="acfg")
    asset_transactions = response['transactions']

    # get frozen state of assets
    response_frozen = indexerConnection.account_info(address=address)
    frozen_asset_info = response_frozen['account']['assets']
    print(json.dumps(frozen_asset_info, indent=2, sort_keys=True))

    frozen_asset = reversed(frozen_asset_info)

    total_assets = []
    asset_txn = []

    # sort the data
    for transaction_info, frozen_state in zip(asset_transactions, frozen_asset):
        params = transaction_info['asset-config-transaction']['params']
        # print(asset_transactions)
        asset_txn.append(transaction_info)
        asset = {
            "asset-name": params.get('name'),
            "unit-name": params.get('unit-name'),
            "url": params.get('url'),
            "total": frozen_state.get('amount'),
            "asset-id": frozen_state.get('asset-id'),
            # "Price": asset_info.get('fee'),
            "frozen-state": frozen_state.get('is-frozen')
        }

        total_assets.append(asset)

    return total_assets


# get the name of the user
def name_by_user_id(user_app_id):

    # search transaction
    app_args = indexerConnection.search_applications(application_id=user_app_id)['applications'][0]['params']['global-state']

    # get the username
    for one_app_args in app_args:
        if one_app_args['key'] == "bmFtZQ==":
            encoded_user_name = one_app_args['value']['bytes']
            user_name = str(base64.b64decode(encoded_user_name)).split('b')[1].replace('\'', "")

            return user_name


# get asset details
def asset_details(asset_id):
    # get asset create transactions
    response = indexerConnection.asset_info(asset_id)
    asset_info = response['asset']
    params = asset_info['params']

    asset = {"asset_name": params.get('name'),
             "unit_name": params.get('unit-name'),
             "url": params.get('url'),
             "total": params.get('total'),
             "asset_id": asset_info.get('index')
             }
    return asset


# get the assets inside the application
def assets_in_wallet(app_id):

    # get address from app id
    address = utilities.CommonFunctions.get_address_from_application(app_id)

    # get frozen state of assets
    response_frozen = indexerConnection.account_info(address=address)
    total_asset_info = response_frozen['account']['assets']

    # create blank array to store loop data
    total_assets = []
    # cashdillo_assets = []

    # loop for searching info for one asset at a time
    for one_asset_info in total_asset_info:
        if one_asset_info.get('amount') > 0:
            asset_detail = indexerConnection.asset_info(one_asset_info['asset-id'])
            one_asset_information = asset_detail['asset']
            one_asset_param = one_asset_information['params']
            asset = {"asset-name": one_asset_param.get('name'),
                     "unit-name": one_asset_param.get('unit-name'),
                     "frozen-state": one_asset_param.get('default-frozen'),
                     "url": one_asset_param.get('url'),
                     "total": one_asset_info.get('amount'),
                     "asset-id": one_asset_information.get('index')
                     }
            total_assets.append(asset)

    # for one_asset in total_assets:
    #     if one_asset['asset_name'] == "Cashdillo" and one_asset['total'] == 1:
    #         cashdillo_assets.append(one_asset)

    return total_assets


# nft marketplace nft list
def assets_in_marketplace(app_id):

    address = encoding.encode_address(encoding.checksum(b'appID' + app_id.to_bytes(8, 'big')))
    # address = "YRUXAUFC7Z5BL3V3XBJ64I5BIN3A4YOJPBLUHGSEDPWNYVGUMOKBIV4N2I"
    # get frozen state of assets
    response_frozen = indexerConnection.account_info(address=address)
    total_asset_info = response_frozen['account']['assets']

    # create blank array to store loop data
    total_assets = []

    # loop for searching info for one asset at a time
    for one_asset_info in total_asset_info:
        if one_asset_info.get('amount') > 0:
            asset_detail = indexerConnection.asset_info(one_asset_info['asset-id'])
            one_asset_information = asset_detail['asset']
            one_asset_param = one_asset_information['params']
            asset = {"asset-name": one_asset_param.get('name'),
                     "unit-name": one_asset_param.get('unit-name'),
                     "frozen-state": one_asset_param.get('default-frozen'),
                     "url": one_asset_param.get('url'),
                     "total": one_asset_info.get('amount'),
                     "asset-id": one_asset_information.get('index')
                     }
            total_assets.append(asset)


    return total_assets


# get the details of the campaign
def campaign(campaign_id):

    # define variables
    invested_amount = 0
    fund_limit = 'None'
    donation_percentage = 'None'

    # get the information of the application
    try:
        campaign_info = indexerConnection.search_applications(application_id=campaign_id)
        campaign_args = campaign_info['applications'][0]['params']['global-state']

        # find the total invested amount in the campaign
        for one_arg in campaign_args:
            key = one_arg['key']
            if "dG90YWxfaW52ZXN0bWVudA==" == key:
                value = one_arg['value']['uint']
                invested_amount = value

        # find the total invested needed in the campaign
        for one_arg in campaign_args:
            key = one_arg['key']
            if "ZnVuZF9saW1pdA==" == key:
                value = one_arg['value']['uint']
                fund_limit = value

    except Exception as error:
        print(error)

    investment_details = {"totalInvested": invested_amount, "fundLimit": fund_limit, "donationPercentage": int(invested_amount/fund_limit * 100)}

    return investment_details


# check milestone payment in campaign
def check_payment_milestone(campaign_app_id):

    # search transactions in blockchain
    campaign_txn_info = indexerConnection.search_transactions(application_id=campaign_app_id, txn_type="appl")
    transactions = campaign_txn_info['transactions']

    # create a blank dictionary
    txn_notes = []

    # search for the notes in the transactions
    for one_transaction in transactions:
        try:
            note = one_transaction['note']
            txn_notes.append(note)
        except Exception as e:
            print(e)

    # check if the claim transaction exist or not
    if "TWlsZXN0b25lIDEgbW9uZXksIGNsYWltZWQ=" in txn_notes:
        return "True"
    else:
        return "False"


# check milestone payment in campaign
def check_payment_milestone_2(campaign_app_id):

    # search transactions in blockchain
    campaign_txn_info = indexerConnection.search_transactions(application_id=campaign_app_id, txn_type="appl")
    transactions = campaign_txn_info['transactions']

    # create a blank dictionary
    txn_notes = []

    # search for the notes in the transactions
    for one_transaction in transactions:
        try:
            note = one_transaction['note']
            txn_notes.append(note)
        except Exception as e:
            print(e)

    # check if the claim transaction exist or not
    if "TWlsZXN0b25lIDIgbW9uZXksIGNsYWltZWQ=" in txn_notes:
        return "True"
    else:
        return "False"


# check milestone payment in campaign for API
def check_payment_milestone_again(campaign_app_id):

    # search transactions in blockchain
    campaign_txn_info = indexerConnection.search_transactions(application_id=campaign_app_id, txn_type="appl")
    transactions = campaign_txn_info['transactions']

    # create a blank dictionary
    txn_notes = []

    # search for the notes in the transactions
    for one_transaction in transactions:
        try:
            note = one_transaction['note']
            txn_notes.append(note)
        except Exception as e:
            print(e)

    invested_amount_in_campaign = int(campaign(campaign_app_id)['totalInvested'])

    # check if the claim transaction exist or not
    if "TWlsZXN0b25lIDEgbW9uZXksIGNsYWltZWQ=" in txn_notes and invested_amount_in_campaign > 0:
        return {"initial_payment_claimed": "TRUE"}
    else:
        return {"initial_payment_claimed": "FALSE"}


# check nft in investor wallet
def list_investors(campaign_id):

    # get the wallet address of the campaign
    campaign_wallet_address = encoding.encode_address(encoding.checksum(b'appID' + int(campaign_id).to_bytes(8, 'big')))

    # search investment done in campaign
    nft_search = indexerConnection.search_transactions(address=campaign_wallet_address, txn_type="pay")
    transactions = nft_search['transactions']

    # create a blank dictionary for loops
    investors_in_campaign = []

    # search for the notes in the transactions
    for one_transaction in transactions:
        if 'note' in one_transaction:
            try:
                # get the address, user app id and the investment amount
                investment_by_address = one_transaction['payment-transaction']['amount']
                txn_note = one_transaction['note']
                bytes_user_app_id = str(base64.b64decode(txn_note)).split(":")[1]
                user_app_id = int(re.search(r'\d+', bytes_user_app_id).group())

                # append the information to the dictionary
                one_investment = {'invested': investment_by_address, "user_app_id": user_app_id}

                if len(investors_in_campaign) > 0:
                    for one_info in investors_in_campaign:

                        if one_investment['user_app_id'] == one_info['user_app_id']:
                            one_info['invested'] = one_investment['invested'] + one_info['invested']
                            break
                        else:
                            investors_in_campaign.append(one_investment)
                            break

                else:
                    investors_in_campaign.append(one_investment)
            except Exception as error:
                print(error)

    # get the top investment done in the campaign
    top_investors = sorted(investors_in_campaign, key=operator.itemgetter("invested"))

    return top_investors[::-1]


# nft list in campaign wallet address
def nft_in_wallet(campaign_id):

    campaign_wallet_address = encoding.encode_address(encoding.checksum (b'appID' + campaign_id.to_bytes (8, 'big')))
    search_nft = indexerConnection.account_info(address=campaign_wallet_address)
    print(json.dumps(search_nft, indent=2, sort_keys=True))

    return search_nft


# check the nft claim by user
def check_claim_nft(user_app_id, campaign_app_id):

    # get the top 10 investors list
    top_investors = list_investors(campaign_app_id)[:10]
    list_len = len(top_investors)
    # get the top investor
    top_investor = top_investors[0]['user_app_id']

    # create blank dictionary
    nft_user_details = []

    # check if the user can claim nft
    if list_len > 0 and top_investor == user_app_id:
        result = {"can_claim_NFT": "True"}
        nft_user_details.append(result)

    else:
        final_result = {"can_claim_NFT": "False"}
        nft_user_details.append(final_result)

    # find how many times user can claim the nft and how many times user has claimed the nft
    try:
        if nft_user_details[0]['can_claim_NFT'] == "True":

            # get the address of the user and the nft of the campaign
            user_wallet_address = utilities.CommonFunctions.get_address_from_application(top_investor)
            nft_asset_id = nft_in_campaign(campaign_app_id)

            # has the user claim the nft
            try:
                txns = indexerConnection.search_transactions(address=user_wallet_address, address_role='receiver',
                                                             asset_id=nft_asset_id)['transactions']
                # transaction for claimed NFT
                if len(txns) > 0:
                    for one_txn in txns:
                        try:
                            if one_txn['note'] == "TkZUIENsYWltZWQ=":
                                result = {"claimed_nft": "True"}
                                nft_user_details.append(result)
                                break
                            else:
                                result = {"claimed_nft": "False"}
                                nft_user_details.append(result)
                                break
                        except Exception as er:
                            print(er)
                else:
                    final_result = {"claimed_nft": "False"}
                    nft_user_details.append(final_result)
            except Exception as error:
                print(error)

                # Give the NFT to top investor
                if nft_user_details[1]['claimed_nft'] == "False" and user_wallet_address == top_investor:
                    result = {'NFT amount user can claim': 1}
                    nft_user_details.append(result)
                else:
                    pass

    except Exception as Error:
        print(Error)

    return nft_user_details


# get nft in the campaign
def nft_in_campaign(campaign_app_id):

    # get the address of the campaign
    campaign_wallet_address = encoding.encode_address(encoding.checksum (b'appID' + int(campaign_app_id).to_bytes (8, 'big')))
    asset_id = 0

    try:
        # search the wallet information
        asset_id = indexerConnection.account_info(address=campaign_wallet_address)['account']['assets'][0]['asset-id']
    except Exception as Error:
        print(Error)

    return asset_id


# get the nft amount left in campaign
def nft_amt_in_campaign(campaign_app_id):

    # get the address of the campaign
    campaign_wallet_address = encoding.encode_address(encoding.checksum (b'appID' + campaign_app_id.to_bytes (8, 'big')))
    asset_amount = 0

    try:
        # search the wallet information
        asset_amount = indexerConnection.account_info(address=campaign_wallet_address)['account']['assets'][0]['amount']
    except Exception as Error:
        print(Error)

    return asset_amount


# get nft in the campaign
def nft_info_in_campaign(campaign_app_id):

    # get the address of the campaign
    campaign_wallet_address = encoding.encode_address(encoding.checksum (b'appID' + campaign_app_id.to_bytes (8, 'big')))
    asset_amount = 0

    try:
        # search the wallet information
        asset_info = indexerConnection.account_info(address=campaign_wallet_address)['account']['assets'][0]
        asset_amount = asset_info['amount']
    except Exception as Error:
        print(Error)

    return asset_amount


# get nft in the campaign
def check_nft_in_campaign(campaign_app_id):

    # get the address of the campaign
    campaign_wallet_address = encoding.encode_address(encoding.checksum (b'appID' + campaign_app_id.to_bytes (8, 'big')))

    # search the wallet information
    asset_id = indexerConnection.account_info(address=campaign_wallet_address)['account']['assets'][0]['asset-id']

    if asset_id:
        return "True"
    else:
        return "False"


# check the campaign type
def campaign_type(campaign_id):

    # get the details of the campaign
    campaign_info = indexerConnection.search_applications(application_id=campaign_id)
    campaign_args = campaign_info['applications'][0]['params']['global-state']

    # fund category ids
    donation = ['6231d702b971347ba6dec133', '623d564ce1b5659d7e3de3f0']
    reward = ['623d5641e1b5659d7e3de3ea', '6225a3097cd8ef00a1fa0d8b']

    # find the fund category of the campaign
    for one_arg in campaign_args:
        key = one_arg['key']
        if "ZnVuZGluZ19jYXRlZ29yeQ==" == key:
            value = one_arg['value']['bytes']
            fund_category = str(base64.b64decode(value)).replace("b'6", "6").replace("'", "")

            if fund_category == donation[0] or fund_category == donation[1]:
                return "Donation"
            elif fund_category == reward[0] or fund_category == reward[1]:
                return "Reward"


# check if the campaign has ended
def campaign_end(campaign_app_id):

    # get the investment of the campaign
    campaign_investment = campaign(campaign_app_id)

    # get the details of the campaign
    campaign_info = indexerConnection.search_applications(application_id=campaign_app_id)
    campaign_args = campaign_info['applications'][0]['params']['global-state']

    # get the variable
    end_time = []

    # get the end time value
    for one_arg in campaign_args:
        key = one_arg['key']
        if "ZW5kX3RpbWU=" == key:
            value = one_arg['value']['uint']
            end_time.append(value)

    # get realtime second
    current_time = utilities.CommonFunctions.Today_seconds()

    if campaign_investment['fundLimit'] == campaign_investment['totalInvested'] or current_time > end_time[0]:
        return "ended"
    else:
        return "not ended"


# decode params
def decode(text):
    bytes_decoded_string = base64.b64decode(text)
    str_decoded_string = str(bytes_decoded_string, 'utf-8')
    return str_decoded_string


# get the key's value for an application
def app_param_value(app_id, key=None):

    app_details = indexerConnection.applications(app_id)
    params_list = app_details['application']['params']['global-state']
    sorted_params = []

    for one_param in params_list:
        encoded_key = one_param['key']
        decoded_key = decode(encoded_key)

        try:
            if one_param['value']['type'] == 2:
                decoded_value = one_param['value']['uint']
            else:
                encoded_value = one_param['value']['bytes']
                decoded_value = decode(encoded_value)

            sorted_params.append({decoded_key: decoded_value})
        except Exception as Error:
            print(Error)

    if key:
        for arg in sorted_params:
            for one_item in arg:
                if one_item == key:
                    return arg.get(key)
    else:
        return sorted_params


# search number of grant managers created by the grant creator
def grant_manager_number_by_grant_creator(creator_app_id):

    response = indexerConnection.search_transactions(application_id=creator_app_id, txn_type='appl')
    app_txns = response['transactions']
    grant_manager_number = 0

    for one_txn in app_txns:
        try:
            if one_txn['note'] == "Q3JlYXRpbmcgbWFuYWdlciBmb3IgQ2FzaGRpbGxv":
                grant_manager_number += 1
        except Exception as error:
            print(error)

    return grant_manager_number


# search number of grants created by the grant creator
def grant_number_by_grant_creator(creator_app_id):

    response = indexerConnection.search_transactions(application_id=creator_app_id, txn_type='appl')
    app_txns = response['transactions']
    grant_manager_number = 0

    for one_txn in app_txns:
        try:
            if one_txn['note'] == "Q3JlYXRpbmcgR3JhbnQ=":
                grant_manager_number += 1
        except Exception as error:
            print(error)

    return grant_manager_number


# check the min and max balance
def balance(client, app_id):
    wallet_address = encoding.encode_address(encoding.checksum(b'appID' + app_id.to_bytes(8, 'big')))
    account_i = client.account_info(wallet_address)
    locked_balance = account_i['min-balance']
    account_balance = account_i['amount']
    print(f"min: {locked_balance}")
    print(f"max: {account_balance}")

    return {"min": locked_balance, "max": account_balance}


# get the total budget and given grant percentage
def percentage_grant(grant_app_id):

    total_budget = app_param_value(grant_app_id, 'total_budget')
    given_grant = app_param_value(grant_app_id, 'given_grant')
    percentage_calculated = given_grant/total_budget * 100

    return {'grantPercentage': str(percentage_calculated)}
