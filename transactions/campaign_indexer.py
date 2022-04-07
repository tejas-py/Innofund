import json
import API.connection

# connect to the indexer API
indexerConnection = API.connection.connect_indexer()


# search total campaigns in the node(Application-campaign)
def total_campaign():
    response = indexerConnection.search_transactions(txn_type="appl")#, min_amount=1999, max_amount=3000)
    campaign_info = json.dumps(response, indent=2, sort_keys=True)
    return campaign_info


# search total campaigns of the particular user
def campaign_by_user(address):
    response = indexerConnection.search_transactions_by_address(address=address, txn_type="appl")
    user_campaign_info = json.dumps(response, indent=2, sort_keys=True)
    return user_campaign_info


# search account information of the user
def address_info(address):
    response = indexerConnection.account_info(address)
    account_info = json.dumps(response, indent=2, sort_keys=True)
    return account_info


if __name__ == '__main__':

    campaign_details = total_campaign()
    txn = json.loads(campaign_details)
    new_data = txn['transactions']
    data = json.dumps(new_data, indent=2, sort_keys=True)
    data_txn = list(data)

    print(data_txn)



