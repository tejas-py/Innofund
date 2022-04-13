import json
import API.connection


indexerConnection = API.connection.connect_indexer()


# get total assets on the nodes
def total_assets_by_admin(admin):
    response = indexerConnection.search_assets(creator=admin)
    asset_info = json.dumps(response, indent=2, sort_keys=True)
    return asset_info


# get account information for a particular address
def account_info(address):
    response = indexerConnection.account_info(address=address)
    asset_info_by_address = json.dumps(response, indent=2, sort_keys=True)
    return asset_info_by_address

