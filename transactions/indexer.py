import base64
import json
import operator
import re
from algosdk import encoding
from API import connection
import utilities.CommonFunctions

# connect to the indexer API
indexerConnection = connection.connect_indexer()


# get total assets on the nodes
def total_assets_by_admin(admin):
    print(f"Total assets minted by {admin}...")
    response = indexerConnection.search_assets(creator=admin)
    asset_info = json.dumps(response, indent=2, sort_keys=True)
    return asset_info


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

    # get the creator of the asset
    creator = params.get('creator')
    asset_fee = indexerConnection.search_transactions_by_address(address=creator, txn_type="acfg", asset_id = asset_id)
    asset_transaction = asset_fee['transactions'][0]

    asset = {"asset-name": params.get('name'),
             "unit-name": params.get('unit-name'),
             "url": params.get('url'),
             "total": params.get('total'),
             "asset-id": asset_info.get('index'),
             "Price": asset_transaction.get('fee')
             }

    return asset



# check if the milestone start transaction exist or not
def assets_in_wallet(app_id):

    # get address from app id
    address = utilities.CommonFunctions.get_address_from_application(app_id)

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
                     "total":one_asset_info.get('amount'),
                     "asset-id": one_asset_information.get('index')
                     }
            total_assets.append(asset)


    return total_assets


# get the details of the campaign
def campaign(campaign_id):

    # define variables
    invested_amount = "None"
    fund_limit = "None"


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

    investment_details = {"totalInvested": invested_amount, "fundLimit": fund_limit}

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

    # check if the claim transaction exist or not
    if "TWlsZXN0b25lIDEgbW9uZXksIGNsYWltZWQ=" in txn_notes:
        return {"initial_payment_claimed": "TRUE"}
    else:
        return {"initial_payment_claimed": "FALSE"}


# check nft in investor wallet
def list_investors(campaign_id):

    # get the wallet address of the campaign
    campaign_wallet_address = encoding.encode_address(encoding.checksum (b'appID' + campaign_id.to_bytes (8, 'big')))

    # search investment done in campaign
    nft_search = indexerConnection.search_transactions(address=campaign_wallet_address, txn_type="pay")
    transactions = nft_search['transactions']
    print(transactions)

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
                one_investment = {'invested': investment_by_address, "user_app_id": user_app_id, "user_name": name_by_user_id(user_app_id)}

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

    # create blank dictionary
    nft_user_details = []

    # check if the user can claim nft
    if list_len > 0:
        # check if the user has invested in the campaign
        for one_investment_info in top_investors:
            if user_app_id == one_investment_info['user_app_id']:
                result = {"can_claim_NFT": "True"}
                nft_user_details.append(result)
                break
    else:
        final_result = {"can_claim_NFT": "False"}
        nft_user_details.append(final_result)

    # find how many times user can claim the nft and how many times user has claimed the nft
    try:
        if nft_user_details[0]['can_claim_NFT'] == "True":

            # get the address of the user and the nft of the campaign
            user_wallet_address = utilities.CommonFunctions.get_address_from_application(user_app_id)
            nft_asset_id = nft_in_campaign(campaign_app_id)

            # has the user claim the nft
            try:
                txns = indexerConnection.search_transactions(address=user_wallet_address, address_role='receiver', asset_id=nft_asset_id)['transactions']
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

            # for top investors' length to 10
            if list_len == 10:
                result1 = {'NFT amount user can claim': 1}
                nft_user_details.append(result1)

            # for top investors' length between 5 and 9
            if 5 <= list_len <= 9:
                if user_app_id == top_investors[0]['user_app_id'] or user_app_id == top_investors[1]['user_app_id'] or \
                        user_app_id == top_investors[2]['user_app_id'] or user_app_id == top_investors[3]['user_app_id']\
                        or user_app_id == top_investors[4]['user_app_id'] or user_app_id == top_investors[5]['user_app_id']:
                    result2={'NFT amount user can claim':2}
                    nft_user_details.append (result2)
                else:
                    result2={'NFT amount user can claim':1}
                    nft_user_details.append (result2)

            # for top investors' length equal to 4
            if list_len == 4:
                if user_app_id == top_investors[0]['user_app_id'] or user_app_id == top_investors[1]['user_app_id']:
                    result3={'NFT amount user can claim':3}
                    nft_user_details.append (result3)
                else:
                    result3={'NFT amount user can claim':2}
                    nft_user_details.append (result3)

            # for top investors' length equal to 3
            if list_len == 3:
                if user_app_id == top_investors[0]['user_app_id']:
                    result4={'NFT amount user can claim':4}
                    nft_user_details.append (result4)
                else:
                    result4={'NFT amount user can claim':3}
                    nft_user_details.append (result4)

            # for top investors' length equal to 2
            if list_len == 2:
                result5 = {'NFT amount user can claim': 5}
                nft_user_details.append(result5)

            # for top investors' length equal to 2
            if list_len == 1:
                result5 = {'NFT amount user can claim': 10}
                nft_user_details.append(result5)

    except Exception as Error:
        print(Error)

    return nft_user_details


# get nft in the campaign
def nft_in_campaign(campaign_app_id):

    # get the address of the campaign
    campaign_wallet_address = encoding.encode_address(encoding.checksum (b'appID' + campaign_app_id.to_bytes (8, 'big')))

    # search the wallet information
    asset_id = indexerConnection.account_info(address=campaign_wallet_address)['account']['assets'][0]['asset-id']

    return asset_id


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

    # find the fund category of the campaign
    for one_arg in campaign_args:
        key = one_arg['key']
        if "ZnVuZGluZ19jYXRlZ29yeQ==" == key:
            value = one_arg['value']['bytes']
            fund_category = str(base64.b64decode(value)).replace('b\'', "").replace('\'', "")
            if fund_category == "6231d702b971347ba6dec133":
                return "Donation"
            elif fund_category == "6225a3097cd8ef00a1fa0d8b":
                return "Reward"
