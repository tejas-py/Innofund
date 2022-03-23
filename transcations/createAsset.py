from algosdk.future import transaction
from billiard.five import string
import utilities.CommonFunctions
from algosdk import account


# create new application
def create_asset(client, private_key, total_nft, unit_name, asset_name, file_path, manager):

    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()

    txn = transaction.AssetConfigTxn(sender=sender, sp=params, total=total_nft, default_frozen=False,
                                     unit_name=unit_name,
                                     asset_name=asset_name, manager=manager,
                                     reserve=manager, freeze=manager, clawback=manager, url=file_path, decimals=0)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    utilities.CommonFunctions.wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    asset_id = transaction_response['asset-index']
    print("Created new asset-id: ", asset_id)

    return string(asset_id)
