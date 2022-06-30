# This transaction contains:
# 1. List total campaigns in the node(Application-campaign).
# 2. List total campaigns of the particular user.
# 3. List out all the assets created by admin.
# 4. List information of a particular address.

import json
from API import connection
import utilities.CommonFunctions
from algosdk.v2client import indexer

# connect to the indexer API
indexerConnection = connection.connect_indexer()


# search total campaigns in the node(Application-campaign)
def total_campaign():
    response = indexerConnection.search_transactions(txn_type="appl")
    campaign_info = json.dumps(response, indent=2, sort_keys=True)
    return campaign_info


# search total campaigns of the particular user
def campaign_by_user(address):
    response = indexerConnection.search_transactions_by_address(address=address, txn_type="appl")
    user_campaign_info = json.dumps(response, indent=2, sort_keys=True)
    return user_campaign_info


# get total assets on the nodes
def total_assets_by_admin(admin):
    print(f"Total assets minted by {admin}...")
    response = indexerConnection.search_assets(creator=admin)
    asset_info = json.dumps(response, indent=2, sort_keys=True)
    return asset_info


# get account information for a particular address
def account_info(address):
    response = indexerConnection.account_info(address=address)
    asset_info_by_address = json.dumps(response, indent=2, sort_keys=True)
    return asset_info_by_address


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
        asset_detail = indexerConnection.asset_info(one_asset_info['asset-id'])
        one_asset_information = asset_detail['asset']
        one_asset_param = one_asset_information['params']
        asset = {"asset-name": one_asset_param.get('name'),
                 "unit-name": one_asset_param.get('unit-name'),
                 "frozen-state": one_asset_param.get('default-frozen'),
                 "url": one_asset_param.get('url'),
                 "total": one_asset_param.get('total'),
                 "asset-id": one_asset_information.get('index'),
                 }
        total_assets.append(asset)

    return total_assets
