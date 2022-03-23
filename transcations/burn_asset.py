from algosdk.future import transaction
from billiard.five import string
import utilities.CommonFunctions
from algosdk import account


# burn asset
def burn_asset(client, private_key, asset_id):

    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()

    txn = transaction.AssetConfigTxn(sender=sender, sp=params, index=asset_id, strict_empty_address_check=False)

    stxn = txn.sign(private_key)
    txid = client.send_transaction(stxn)
    print("Signed transaction with txID: {}".format(txid))

    # Wait for the transaction to be confirmed
    confirmed_txn = utilities.CommonFunctions.wait_for_confirmation(client, txid)
    print("TXID: ", txid)
    print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))

    return string(txid)
