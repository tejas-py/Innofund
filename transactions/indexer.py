# This transaction contains:
# 1. List total campaigns in the node(Application-campaign).
# 2. List total campaigns of the particular user.
# 3. List out all the assets created by admin.
# 4. List information of a particular address.

import json
from API import connection
import utilities.CommonFunctions

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
def get_minted_asset_transaction(app_id):

    # get address from app id
    address = utilities.CommonFunctions.get_address_from_application(app_id)

    # get asset create transactions
    response = indexerConnection.search_transactions_by_address(address=address, txn_type="acfg")
    asset_transactions = response['transactions']

    # get frozen state of assets
    response_frozen = indexerConnection.account_info(address=address)
    frozen_asset_info = response_frozen['account']['assets']
    frozen_asset = reversed(frozen_asset_info)

    total_assets = []

    # sort the data
    for transaction_info, frozen_state in zip(asset_transactions, frozen_asset):
        params = transaction_info['asset-config-transaction']['params']
        asset_info = transaction_info
        asset = {
            "asset-name": params.get('name'),
            "unit-name": params.get('unit-name'),
            "url": params.get('url'),
            "total": frozen_state.get('amount'),
            "asset-id": frozen_state.get('asset-id'),
            "Price": asset_info.get('fee'),
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
