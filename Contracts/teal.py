from algosdk import encoding
from pyteal import *


# convert pyteal to teal (application)
def to_teal(client, smart_contract):

    # First convert the PyTeal to TEAL
    teal_campaign = compileTeal(smart_contract, Mode.Application, version=6)

    # Next compile our TEAL to bytecode. (it's returned in base64)
    b64_campaign = client.compile(teal_campaign)['result']

    # Lastly decode the base64.
    prog_campaign = encoding.base64.b64decode(b64_campaign)

    return prog_campaign


def to_teal_sign(client, smart_contract):

    # First convert the PyTeal to TEAL
    teal_campaign = compileTeal(smart_contract, Mode.Signature, version=6)

    # Next compile our TEAL to bytecode. (it's returned in base64)
    b64_campaign = client.compile(teal_campaign)['result']

    # Lastly decode the base64.
    prog_campaign = encoding.base64.b64decode(b64_campaign)

    return prog_campaign

