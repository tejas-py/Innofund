from algosdk import mnemonic
import base64
import os
import time
from algosdk.v2client import indexer



# compile program used to compile the source code, used when new application is created
def compile_program(client, source_code):
    compile_response = client.compile(source_code.decode('utf-8'))
    return base64.b64decode(compile_response['result'])


# helper function that converts a mnemonic passphrase into a private signing key
def get_private_key_from_mnemonic(mn):
    private_key = mnemonic.to_private_key(mn)
    return private_key


# helper function that waits for a given txid to be confirmed by the network
def wait_for_confirmation(client, txid):
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
        print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
        return txinfo


# load resource used for logic signature
def load_resource(res):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, res)
    with open(path, "rb") as fin:
        data = fin.read()
    return data


def Today_seconds():
    today_time = time.localtime()
    seconds_today_time = time.mktime(today_time)
    today_seconds = int(seconds_today_time)
    return today_seconds


def Check_app_creator_address(app_id, check_address):

    # connect to indexer
    headers = {
        "X-API-Key": "K7DgVll3W19DdHA3FTduX4XZTuCvTFf32HXUP5E4",
    }
    myindexer = indexer.IndexerClient(indexer_token="K7DgVll3W19DdHA3FTduX4XZTuCvTFf32HXUP5E4",
                                      indexer_address="https://testnet-algorand.api.purestake.io/idx2",
                                      headers=headers)

    # Get the creator address of the application
    response = myindexer.applications(app_id)
    app_info = response['application']
    app_param_info = app_info['params']

    if check_address == app_param_info['creator']:
        return 'Match'
    else:
        return 'Address is not same as the creator address of the campaign'
