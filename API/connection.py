from algosdk.v2client import algod


def algo_conn():
    algod_address = "https://testnet-algorand.api.purestake.io/ps2"
    algod_token = "K7DgVll3W19DdHA3FTduX4XZTuCvTFf32HXUP5E4"
    headers = {"X-API-Key": algod_token}
    conn = algod.AlgodClient(algod_token, algod_address, headers)

    return conn


